
from rest_framework import viewsets, serializers
from .models import Airline, Flight, Passenger, Rate, Ticket
from .serializers import *
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Avg, Max, Min

class AirlineViewSet(viewsets.ModelViewSet):
    queryset = Airline.objects.all()
    serializer_class = AirlineSerializer

    class StatsSerializer(serializers.Serializer):
        count = serializers.IntegerField()

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request):
        stats = Airline.objects.aggregate(
            count=Count("*")
        )
        serializer = self.StatsSerializer(stats)
        return Response(serializer.data)

class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer

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

class PassengerViewSet(viewsets.ModelViewSet):
    queryset = Passenger.objects.all()
    serializer_class = PassengerSerializer

    class StatsSerializer(serializers.Serializer):
        count = serializers.IntegerField()
        with_phone = serializers.IntegerField()
        without_phone = serializers.IntegerField()
        with_photo = serializers.IntegerField()

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request):
        total = Passenger.objects.count()
        with_phone = Passenger.objects.exclude(phone__isnull=True).exclude(phone='').count()
        with_photo = Passenger.objects.exclude(picture__isnull=True).exclude(picture='').count()
        
        stats = {
            'count': total,
            'with_phone': with_phone,
            'without_phone': total - with_phone,
            'with_photo': with_photo
        }
        serializer = self.StatsSerializer(stats)
        return Response(serializer.data)

class RateViewSet(viewsets.ModelViewSet):
    queryset = Rate.objects.all()
    serializer_class = RateSerializer

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

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    class StatsSerializer(serializers.Serializer):
        count = serializers.IntegerField()
        today_count = serializers.IntegerField()
        with_seat = serializers.IntegerField()
        without_seat = serializers.IntegerField()

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request):
        from django.utils import timezone
        from django.db.models import Q
        
        total = Ticket.objects.count()
        today = Ticket.objects.filter(booking_date__date=timezone.now().date()).count()
        with_seat = Ticket.objects.exclude(seat__isnull=True).exclude(seat='').count()
        
        stats = {
            'count': total,
            'today_count': today,
            'with_seat': with_seat,
            'without_seat': total - with_seat
        }
        serializer = self.StatsSerializer(stats)
        return Response(serializer.data)
