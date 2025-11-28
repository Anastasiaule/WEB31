from rest_framework import viewsets, serializers, permissions
from .models import Airline, Flight, Passenger, Rate, Ticket
from .serializers import *
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Avg, Max, Min
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied


# ===================== ПРАВИЛА ДОСТУПА ======================

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Обычный юзер видит только свои данные.
    Суперпользователь видит всё.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if hasattr(obj, 'user'):
            return obj.user == request.user

        if hasattr(obj, 'passenger') and hasattr(obj.passenger, 'user'):
            return obj.passenger.user == request.user

        return False


class IsSuperUserOrReadOnly(permissions.BasePermission):
    """
    Только суперюзер может изменять данные.
    Обычный пользователь — только читать.
    """

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
        serializer = self.StatsSerializer(stats)
        return Response(serializer.data)


# ========================== USER =============================

class UserViewSet(viewsets.GenericViewSet):
    permission_classes = []

    @action(detail=False, url_path="info", methods=["GET"])
    def get_info(self, request, *args, **kwargs):
        return Response({
            "username": request.user.username,
            "is_authenticated": request.user.is_authenticated,
            "is_staff": request.user.is_staff,
            "is_superuser": request.user.is_superuser,  # <- добавлено
        })

    @action(detail=False, url_path="login", methods=["POST"])
    def login_user(self, request, *args, **kwargs):
        username = self.request.data['username']
        password = self.request.data['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({'success': True})
        return Response({'success': False})

    @action(detail=False, url_path="logout", methods=["POST"])
    def logout_user(self, request, *args, **kwargs):
        request.session.flush()
        logout(request)
        return Response({'success': True})


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
        serializer = self.StatsSerializer(stats)
        return Response(serializer.data)


# ========================= PASSENGER ==========================

class PassengerViewSet(viewsets.ModelViewSet):
    serializer_class = PassengerSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly, IsSuperUserOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Passenger.objects.all()
        return Passenger.objects.filter(user=self.request.user)

    class StatsSerializer(serializers.Serializer):
        count = serializers.IntegerField()
        with_phone = serializers.IntegerField()
        without_phone = serializers.IntegerField()
        with_photo = serializers.IntegerField()

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request):
        user_passengers = self.get_queryset()

        total = user_passengers.count()
        with_phone = user_passengers.exclude(phone__isnull=True).exclude(phone='').count()
        with_photo = user_passengers.exclude(picture__isnull=True).exclude(picture='').count()

        stats = {
            'count': total,
            'with_phone': with_phone,
            'without_phone': total - with_phone,
            'with_photo': with_photo
        }
        serializer = self.StatsSerializer(stats)
        return Response(serializer.data)


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
        serializer = self.StatsSerializer(stats)
        return Response(serializer.data)


# ============================ TICKET ============================

class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Ticket.objects.all()

        return Ticket.objects.filter(passenger__user=self.request.user)

    # ----- Логика действий -----

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

            # обычному пользователю нельзя менять пассажира
            if "passenger" in serializer.validated_data:
                del serializer.validated_data["passenger"]

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
        user_tickets = self.get_queryset()

        total = user_tickets.count()
        today = user_tickets.filter(booking_date__date=timezone.now().date()).count()
        with_seat = user_tickets.exclude(seat__isnull=True).exclude(seat='').count()

        stats = {
            'count': total,
            'today_count': today,
            'with_seat': with_seat,
            'without_seat': total - with_seat
        }
        serializer = self.StatsSerializer(stats)
        return Response(serializer.data)
