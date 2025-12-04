from rest_framework import viewsets, permissions  
from rest_framework.decorators import action   
from rest_framework.response import Response    
from rest_framework.exceptions import PermissionDenied
from django.db.models import Count, Avg, Max, Min 
from django.contrib.auth import authenticate, login, logout 
from django.utils import timezone         
from .models import Airline, Flight, Passenger, Rate, Ticket
from .serializers import *

# проверка прав доступа
class IsSuperUserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True  # Все пользователи могут читать
        return request.user.is_superuser  # Только суперюзеры могут изменять


# авиакомпании
class AirlineViewSet(viewsets.ModelViewSet):
    queryset = Airline.objects.all()  
    serializer_class = AirlineSerializer  
    permission_classes = [IsSuperUserOrReadOnly]  # Применяем наши правила доступа

    class StatsSerializer(serializers.Serializer):
        count = serializers.IntegerField()  # Поле для количества авиакомпаний

    # Декоратор @action создает дополнительный URL /api/airlines/stats/
    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request):

        # aggregate() выполняет агрегатные операции над данными
        stats = Airline.objects.aggregate(count=Count("*"))
        # Возвращаем ответ в формате JSON
        return Response(self.StatsSerializer(stats).data)


# юзеры
class UserViewSet(viewsets.GenericViewSet):

    permission_classes = []  # Не требует авторизации, доступно всем

    @action(detail=False, url_path="info", methods=["GET"])
    def get_info(self, request):

        return Response({
            "username": request.user.username,  # Имя пользователя
            "is_authenticated": request.user.is_authenticated,  # Авторизован ли
            "is_staff": request.user.is_staff,  # Является ли сотрудником
            "is_superuser": request.user.is_superuser,  # Является ли суперпользователем
        })

    @action(detail=False, url_path="login", methods=["POST"])
    def login_user(self, request):
 
        # Получаем логин и пароль из тела запроса
        username = request.data.get("username")
        password = request.data.get("password")

        # Проверяем правильность логина и пароля
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return Response({"success": True})  # Успешный вход
        else:
            return Response({"success": False})  # Неверные данные

    @action(detail=False, url_path="logout", methods=["POST"])
    def logout_user(self, request):
       
        # Очищаем сессию и выходим
        request.session.flush()  # Удаляем все данные сессии
        logout(request)  # Выход из системы
        return Response({"success": True})


# рейсы
class FlightViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с рейсами.
    """
    queryset = Flight.objects.all()  # Все рейсы из базы
    serializer_class = FlightSerializer  # Сериализатор для рейсов
    permission_classes = [IsSuperUserOrReadOnly]  # Только суперюзер может изменять

    # Класс для сериализации статистики по рейсам
    class StatsSerializer(serializers.Serializer):
        count = serializers.IntegerField() 
        avg_price = serializers.FloatField() 
        max_price = serializers.FloatField() 
        min_price = serializers.FloatField() 

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request):
        # Выполняем несколько агрегатных операций за один запрос
        stats = Flight.objects.aggregate(
            count=Count("*"),   
            avg_price=Avg("price"),
            max_price=Max("price"),  
            min_price=Min("price"),  
        )
        return Response(self.StatsSerializer(stats).data)


# пассажиры
class PassengerViewSet(viewsets.ModelViewSet):
    serializer_class = PassengerSerializer
    permission_classes = [permissions.IsAuthenticated]  # Требует авторизации

    def get_queryset(self):
        user = self.request.user  # Получаем текущего пользователя

        # Суперпользователь видит всех пассажиров
        if user.is_superuser:
            qs = Passenger.objects.all()  # Берем всех пассажиров
            
            # Дополнительная фильтрация по пользователю 
            user_id = self.request.query_params.get("user")
            if user_id:
                qs = qs.filter(user_id=user_id)  # Фильтруем по ID пользователя
            return qs

        # Обычный пользователь только своих пассажиров
        return Passenger.objects.filter(user=user)

    def perform_create(self, serializer):
        # Сохраняем пассажира, устанавливая его владельцем текущего пользователя
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        passenger = self.get_object()  # Получаем редактируемого пассажира
        user = self.request.user  # Текущий пользователь
        # Сохраняем изменения
        serializer.save()

    def destroy(self, request, *args, **kwargs):

        passenger = self.get_object()  # Получаем удаляемого пассажира
        user = request.user  # Текущий пользователь
        # Вызываем стандартный метод удаления
        return super().destroy(request, *args, **kwargs)

    # ----- Статистика по пассажирам -----
    class StatsSerializer(serializers.Serializer):
        # Поля для статистики
        count = serializers.IntegerField()   
        with_phone = serializers.IntegerField() 
        without_phone = serializers.IntegerField() 
        with_photo = serializers.IntegerField()  

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request):
        qs = self.get_queryset()  # Используем отфильтрованный список пассажиров

        # Вычисляем различные показатели
        total = qs.count()  # Общее количество пассажиров
        with_phone = qs.exclude(phone__isnull=True).exclude(phone="").count()
        with_photo = qs.exclude(picture__isnull=True).exclude(picture="").count()

        # Формируем данные для ответа
        data = {
            "count": total,
            "with_phone": with_phone,
            "without_phone": total - with_phone,
            "with_photo": with_photo,
        }

        return Response(self.StatsSerializer(data).data)


# тарифы
class RateViewSet(viewsets.ModelViewSet):
    queryset = Rate.objects.all()  # Все тарифы
    serializer_class = RateSerializer
    permission_classes = [IsSuperUserOrReadOnly]  # Только суперюзер может изменять

    # Класс для сериализации статистики по тарифам
    class StatsSerializer(serializers.Serializer):
        count = serializers.IntegerField()
        avg_multiplier = serializers.FloatField()
        max_multiplier = serializers.FloatField() 
        min_multiplier = serializers.FloatField()  

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request):

        # Агрегируем данные по тарифам
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
    permission_classes = [permissions.IsAuthenticated]  # Требует авторизации

    def get_queryset(self):
        # Если пользователь суперюзер - показываем все билеты
        if self.request.user.is_superuser:
            return Ticket.objects.all()

        # Иначе показываем только билеты пассажиров текущего пользователя
        return Ticket.objects.filter(passenger__user=self.request.user)

    # CRUD операции для билетов
    def perform_create(self, serializer):
        # Получаем пассажира из данных формы
        passenger = serializer.validated_data.get("passenger")

        # Если пользователь не суперюзер
        if not self.request.user.is_superuser:
            # Проверяем, что пассажир принадлежит текущему пользователю
            if passenger.user != self.request.user:
                raise PermissionDenied("Вы не можете покупать билет для чужого пассажира.")

        # Сохраняем билет
        serializer.save()

    def perform_update(self, serializer):
        ticket = self.get_object()  # Получаем редактируемый билет

        # Если пользователь не суперюзер
        if not self.request.user.is_superuser:
            # Проверяем, что билет принадлежит пассажиру текущего пользователя
            if ticket.passenger.user != self.request.user:
                raise PermissionDenied("Вы не можете редактировать чужой билет.")

            serializer.validated_data.pop("passenger", None)

        # Сохраняем изменения
        serializer.save()

    def destroy(self, request, *args, **kwargs):

        # Только суперюзер может удалять билеты
        if not request.user.is_superuser:
            raise PermissionDenied("Удаление билетов доступно только администраторам.")

        # Вызываем стандартный метод удаления
        return super().destroy(request, *args, **kwargs)

    #  Статистика по билетам
    class StatsSerializer(serializers.Serializer):
        # Поля для статистики
        count = serializers.IntegerField()      
        today_count = serializers.IntegerField() 
        with_seat = serializers.IntegerField()   
        without_seat = serializers.IntegerField() 

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request):
 
        qs = self.get_queryset()  # Используем отфильтрованный список билетов

        # Вычисляем показатели
        total = qs.count()
        today = qs.filter(booking_date__date=timezone.now().date()).count()
        with_seat = qs.exclude(seat__isnull=True).exclude(seat="").count()

        # Формируем данные для ответа
        data = {
            "count": total,
            "today_count": today,
            "with_seat": with_seat,
            "without_seat": total - with_seat, 
        }

        return Response(self.StatsSerializer(data).data)