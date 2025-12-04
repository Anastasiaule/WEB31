from rest_framework import serializers
from .models import Airline, Flight, Passenger, Rate, Ticket


class AirlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airline
        fields = '__all__'


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = '__all__'


class PassengerSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Passenger
        fields = ['id', 'full_name', 'passport', 'phone', 'picture', 'user']

class RateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rate
        fields = '__all__'


class TicketSerializer(serializers.ModelSerializer):
    passenger_name = serializers.CharField(source='passenger.full_name', read_only=True)
    flight_name = serializers.CharField(source='flight.route', read_only=True)
    rate_name = serializers.CharField(source='rate.name', read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'flight', 'flight_name', 'passenger', 'passenger_name',
                  'rate', 'rate_name', 'seat', 'booking_date']
