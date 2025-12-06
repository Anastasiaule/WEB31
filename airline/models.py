from django.db import models
from django.contrib.auth.models import User 
from django.utils import timezone

# 1. Авиакомпании
class Airline(models.Model):
    name = models.CharField("Авиакомпания", max_length=100)
    picture = models.ImageField("Изображение", null=True, upload_to="airline")

    class Meta:
        verbose_name = "Авиакомпания"
        verbose_name_plural = "Авиакомпании"

    def __str__(self):
        return self.name


# 2. Рейсы
class Flight(models.Model):
    name = models.CharField("Номер рейса", max_length=20)
    route = models.CharField("Маршрут", max_length=100, blank=True)
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE, verbose_name="Авиакомпания", null=True, blank=True)
    price = models.IntegerField("Цена", default=0)
    departure_time = models.DateTimeField("Время вылета", default=timezone.now)
    arrival_time = models.DateTimeField("Время прилета", default=timezone.now)

    class Meta:
        verbose_name = "Рейс"
        verbose_name_plural = "Рейсы"

    def __str__(self):
        return f"{self.name} - {self.route}"

# 3. Пассажиры
class Passenger(models.Model):
    full_name = models.CharField("ФИО пассажира", max_length=100)
    passport = models.CharField("Паспорт", max_length=20)
    phone = models.CharField("Телефон", max_length=15, blank=True)
    picture = models.ImageField("Изображение", null=True, upload_to="passengers", blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь", related_name="passengers") 

    class Meta:
        verbose_name = "Пассажир"
        verbose_name_plural = "Пассажиры"

    def __str__(self):
        return self.full_name


# 4. Тарифы
class Rate(models.Model):
    name = models.CharField("Тариф", max_length=50)
    multiplier = models.FloatField("Коэффициент цены", default=1.0)

    class Meta:
        verbose_name = "Тариф"
        verbose_name_plural = "Тарифы"

    def __str__(self):
        return self.name


# 5. Билеты
class Ticket(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, verbose_name="Рейс")
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE, verbose_name="Пассажир")
    rate = models.ForeignKey(Rate, on_delete=models.CASCADE, verbose_name="Тариф")
    seat = models.CharField("Место", max_length=5, blank=True)
    booking_date = models.DateTimeField("Дата брони", auto_now_add=True)


    class Meta:
        verbose_name = "Билет"
        verbose_name_plural = "Билеты"

    def __str__(self):
        return f"Билет {self.passenger} - {self.flight}"
