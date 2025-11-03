from django.contrib import admin
from .models import Airline, Flight, Passenger, Rate, Ticket


@admin.register(Airline)
class AirlineAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'route', 'airline', 'price', 'departure_time', 'arrival_time']
    list_filter = ['airline']
    search_fields = ['name', 'route']


@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'passport', 'phone', 'user']
    list_filter = ['user']
    search_fields = ['full_name', 'passport']


@admin.register(Rate)
class RateAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'multiplier']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'passenger', 'flight', 'rate', 'seat', 'booking_date', 'user']
    list_filter = ['rate', 'booking_date', 'user']
    search_fields = ['passenger__full_name', 'flight__name']
