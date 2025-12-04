from rest_framework import viewsets, serializers, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.db.models import Count, Avg, Max, Min
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone

from .models import Airline, Flight, Passenger, Rate, Ticket
from .serializers import *


# ===================== ACCESS RULES ======================

class IsSuperUserOrReadOnly(permissions.BasePermission):
    """Только суперюзер может менять. Остальные — только читать."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_superuser


# ========================= AIRLINE ===========================

class AirlineViewSet(viewsets.ModelViewSet):
    queryset = Airline.objects.all()
    serializer_class = AirlineSerializer
    permission_classes = [IsSuperUserOrReadOnly]

    class StatsSerializer(serializers.Serializer):
        count = serializers.IntegerField()

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request):
        stats = Airline.objects.aggregate(count=Count("*"))
        return Response(self.StatsSerializer(stats).data)


# ========================== USER =============================

class UserViewSet(viewsets.GenericViewSet):
    permission_classes = []

    @action(detail=False, url_path="info", methods=["GET"])
    def get_info(self, request):
        return Response({
            "username": request.user.username,
            "is_authenticated": request.user.is_authenticated,
            "is_staff": request.user.is_staff,
            "is_superuser": request.user.is_superuser,
        })

    @action(detail=False, url_path="login", methods=["POST"])
    def login_user(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return Response({"success": True})

        return Response({"success": False})

    @action(detail=False, url_path="logout", methods=["POST"])
    def logout_user(self, request):
        request.session.flush()
        logout(request)
        return Response({"success": True})


# ========================== FLIGHT ===========================

class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    permission_classes = [IsSuperUserOrReadOnly]

    class StatsSerializer(serializers.Serializer):
        count = serializers.IntegerField()
        avg_price = serializers.FloatField()
        max_price = serializers.FloatField()
        min_price = serializers.FloatField()

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request):
        stats = Flight.objects.aggregate(
            count=Count("*"),
            avg_price=Avg("price"),
            max_price=Max("price"),
            min_price=Min("price"),
        )
        return Response(self.StatsSerializer(stats).data)


# ========================= PASSENGER ==========================

class PassengerViewSet(viewsets.ModelViewSet):
    serializer_class = PassengerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # 🟦 Суперпользователь видит всех + может фильтровать по user
        if user.is_superuser:
            qs = Passenger.objects.all()
            user_id = self.request.query_params.get("user")
            if user_id:
                qs = qs.filter(user_id=user_id)
            return qs

        # 🟩 Обычный пользователь: только свои пассажиры
        return Passenger.objects.filter(user=user)

    def perform_create(self, serializer):
        # Обычный пользователь создаёт пассажиров ТОЛЬКО для себя
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        passenger = self.get_object()
        user = self.request.user

        if not user.is_superuser and passenger.user != user:
            raise PermissionDenied("Вы не можете редактировать чужого пассажира.")

        serializer.save()

    def destroy(self, request, *args, **kwargs):
        passenger = self.get_object()
        user = request.user

        if not user.is_superuser and passenger.user != user:
            raise PermissionDenied("Вы не можете удалять чужого пассажира.")

        return super().destroy(request, *args, **kwargs)

    # ----- Статистика -----

    class StatsSerializer(serializers.Serializer):
        count = serializers.IntegerField()
        with_phone = serializers.IntegerField()
        without_phone = serializers.IntegerField()
        with_photo = serializers.IntegerField()

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request):
        qs = self.get_queryset()

        total = qs.count()
        with_phone = qs.exclude(phone__isnull=True).exclude(phone="").count()
        with_photo = qs.exclude(picture__isnull=True).exclude(picture="").count()

        data = {
            "count": total,
            "with_phone": with_phone,
            "without_phone": total - with_phone,
            "with_photo": with_photo,
        }

        return Response(self.StatsSerializer(data).data)


# ============================ RATE ============================

class RateViewSet(viewsets.ModelViewSet):
    queryset = Rate.objects.all()
    serializer_class = RateSerializer
    permission_classes = [IsSuperUserOrReadOnly]

    class StatsSerializer(serializers.Serializer):
        count = serializers.IntegerField()
        avg_multiplier = serializers.FloatField()
        max_multiplier = serializers.FloatField()
        min_multiplier = serializers.FloatField()

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request):
        stats = Rate.objects.aggregate(
            count=Count("*"),
            avg_multiplier=Avg("multiplier"),
            max_multiplier=Max("multiplier"),
            min_multiplier=Min("multiplier"),
        )
        return Response(self.StatsSerializer(stats).data)


# ============================ TICKET ============================

class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Ticket.objects.all()

        return Ticket.objects.filter(passenger__user=self.request.user)

    # ----- CRUD -----

    def perform_create(self, serializer):
        passenger = serializer.validated_data.get("passenger")

        if not self.request.user.is_superuser:
            if passenger.user != self.request.user:
                raise PermissionDenied("Вы не можете покупать билет для чужого пассажира.")

        serializer.save()

    def perform_update(self, serializer):
        ticket = self.get_object()

        if not self.request.user.is_superuser:
            if ticket.passenger.user != self.request.user:
                raise PermissionDenied("Вы не можете редактировать чужой билет.")

            # обычный пользователь не может менять passenger
            serializer.validated_data.pop("passenger", None)

        serializer.save()

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied("Удаление билетов доступно только администраторам.")

        return super().destroy(request, *args, **kwargs)

    # ----- Статистика -----

    class StatsSerializer(serializers.Serializer):
        count = serializers.IntegerField()
        today_count = serializers.IntegerField()
        with_seat = serializers.IntegerField()
        without_seat = serializers.IntegerField()

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request):
        qs = self.get_queryset()

        total = qs.count()
        today = qs.filter(booking_date__date=timezone.now().date()).count()
        with_seat = qs.exclude(seat__isnull=True).exclude(seat="").count()

        data = {
            "count": total,
            "today_count": today,
            "with_seat": with_seat,
            "without_seat": total - with_seat,
        }

        return Response(self.StatsSerializer(data).data)
