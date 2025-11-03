from rest_framework import viewsets, permissions
from .models import Airline, Flight, Passenger, Rate, Ticket
from .serializers import AirlineSerializer, FlightSerializer, PassengerSerializer, RateSerializer, TicketSerializer


class IsOwnerOrAdmin(permissions.BasePermission):
    """Только владелец или админ может видеть/редактировать объект"""
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True
        return getattr(obj, "user", None) == request.user


class AirlineViewSet(viewsets.ModelViewSet):
    queryset = Airline.objects.all()
    serializer_class = AirlineSerializer
    permission_classes = [permissions.IsAuthenticated]


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    permission_classes = [permissions.IsAuthenticated]


class PassengerViewSet(viewsets.ModelViewSet):
    queryset = Passenger.objects.all()
    serializer_class = PassengerSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_superuser:
            user_id = self.request.query_params.get("user")
            if user_id:
                qs = qs.filter(user_id=user_id)
            return qs
        return qs.filter(user=user)


class RateViewSet(viewsets.ModelViewSet):
    queryset = Rate.objects.all()
    serializer_class = RateSerializer
    permission_classes = [permissions.IsAuthenticated]


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_superuser:
            user_id = self.request.query_params.get("user")
            if user_id:
                qs = qs.filter(user_id=user_id)
            return qs
        return qs.filter(user=user)
