from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.db.models import Count, Avg, Max, Min
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.http import HttpResponse
from .models import Airline, Flight, Passenger, Rate, Ticket
from django.contrib.auth.models import User
from .serializers import *
import pandas as pd
from io import BytesIO
import datetime

# проверка прав доступа
class IsSuperUserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_superuser


# авиакомпании
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


# юзеры
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
    
    @action(detail=False, methods=["GET"])
    def list_users(self, request):
        if not request.user.is_superuser:
            return Response({"error": "Доступно только суперпользователям"}, status=403)
        
        users_list = User.objects.all().values('id', 'username', 'email')
        return Response(list(users_list))
    

    @action(detail=False, url_path="login", methods=["POST"])
    def login_user(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return Response({"success": True})
        else:
            return Response({"success": False})

    @action(detail=False, url_path="logout", methods=["POST"])
    def logout_user(self, request):
        request.session.flush()
        logout(request)
        return Response({"success": True})


# рейсы
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

    @action(detail=False, methods=['GET'], url_path='export-excel')
    def export_excel(self, request):
        try:
            flights = Flight.objects.all()
            
            data = []
            for flight in flights:
                data.append({
                    'ID': flight.id,
                    'Номер рейса': flight.name,
                    'Маршрут': flight.route,
                    'Авиакомпания': flight.airline.name if flight.airline else '',
                    'Цена': float(flight.price) if flight.price else 0,
                    'Дата вылета': str(flight.departure_time),
                    'Дата прибытия': str(flight.arrival_time),
                })
            
            df = pd.DataFrame(data)
            
            output = BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Рейсы')
            
            output.seek(0)
            
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            filename = f"flights_{today}.xlsx"
            
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            print(f"Ошибка при экспорте рейсов: {str(e)}")
            return Response(
                {"error": f"Ошибка при экспорте: {str(e)}"}, 
                status=500
            )


# пассажиры
class PassengerViewSet(viewsets.ModelViewSet):
    serializer_class = PassengerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            qs = Passenger.objects.all()
            user_id = self.request.query_params.get("user")
            if user_id:
                qs = qs.filter(user_id=user_id)
            return qs

        return Passenger.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

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

    @action(detail=False, methods=['GET'], url_path='export-excel')
    def export_excel(self, request):
        try:
            qs = self.get_queryset()
            
            data = []
            for passenger in qs:
                data.append({
                    'ID': passenger.id,
                    'ФИО': passenger.full_name,
                    'Паспорт': passenger.passport,
                    'Телефон': passenger.phone or '',
                    'Пользователь': passenger.user.username if passenger.user else ''
                })
            
            df = pd.DataFrame(data)
            
            output = BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Пассажиры')
            
            output.seek(0)
            
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            filename = f"passengers_{today}.xlsx"
            
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            print(f"Ошибка при экспорте пассажиров: {str(e)}")
            return Response(
                {"error": f"Ошибка при экспорте: {str(e)}"}, 
                status=500
            )


# тарифы
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


# билеты
class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Ticket.objects.all()
        return Ticket.objects.filter(passenger__user=self.request.user)

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
            serializer.validated_data.pop("passenger", None)

        serializer.save()

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied("Удаление билетов доступно только администраторам.")
        return super().destroy(request, *args, **kwargs)

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

    @action(detail=False, methods=['GET'], url_path='export-excel')
    def export_excel(self, request):
        try:
            qs = self.get_queryset()
            
            data = []
            for ticket in qs:
                # Рассчитываем цену: цена рейса * множитель тарифа
                flight_price = ticket.flight.price if ticket.flight else 0
                rate_multiplier = ticket.rate.multiplier if ticket.rate else 1.0
                calculated_price = flight_price * rate_multiplier
                
                data.append({
                    'ID': ticket.id,
                    'Пассажир': ticket.passenger.full_name if ticket.passenger else '',
                    'Рейс': ticket.flight.name if ticket.flight else '',
                    'Тариф': ticket.rate.name if ticket.rate else '',
                    'Цена рейса': float(ticket.flight.price) if ticket.flight and ticket.flight.price else 0,
                    'Множитель тарифа': float(ticket.rate.multiplier) if ticket.rate and ticket.rate.multiplier else 1.0,
                    'Итоговая цена': float(calculated_price),
                    'Место': ticket.seat or '',
                    'Дата бронирования': str(ticket.booking_date),
                })
            
            df = pd.DataFrame(data)
            
            output = BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Билеты')
            
            output.seek(0)
            
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            filename = f"tickets_{today}.xlsx"
            
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            print(f"Ошибка при экспорте билетов: {str(e)}")
            return Response(
                {"error": f"Ошибка при экспорте: {str(e)}"}, 
                status=500
            )