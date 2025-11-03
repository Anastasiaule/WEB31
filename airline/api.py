from rest_framework import viewsets
from .models import Airline, Flight, Passenger, Rate, Ticket
from .serializers import *
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Avg, Max, Min
from rest_framework import serializers
class AirlineViewSet(viewsets.ModelViewSet):
    queryset = Airline.objects.all()
    serializer_class = AirlineSerializer

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

class RateViewSet(viewsets.ModelViewSet):
    queryset = Rate.objects.all()
    serializer_class = RateSerializer

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer