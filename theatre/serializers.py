from rest_framework import serializers

from .models import (
    Play,
    Actor,
    Genre,
    TheatreHall,
    Performance,
    Reservation,
    Ticket,
)


class PlaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Play
        fields = ("id", "title", "description", "actors", "genres", "actor_count")


class PlayerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Play
        fields = ("id", "title", "description", "actor_count")


class PlayerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Play
        fields = ("id", "title", "description", "actors", "genres")


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ("id", "first_name", "last_name")


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("id", "name")


class TheatreHallSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheatreHall
        fields = ("id", "name", "rows", "seats_in_row")


class PerformanceSerializer(serializers.ModelSerializer):
    play = PlaySerializer(many=False, read_only=True)

    class Meta:
        model = Performance
        fields = ("id", "play", "theatre_hall", "show_time")


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ("id", "created_at", "user")


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "performance", "reservation")


class TicketListSerializer(TicketSerializer):
    performance = PerformanceSerializer(many=False, read_only=True)
    owner = serializers.CharField(source="reservation.user", read_only=True)

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "performance", "owner")


class TicketDetailSerializer(TicketSerializer):
    performance = PerformanceSerializer(many=False, read_only=True)
    reservation = ReservationSerializer(many=False, read_only=True)

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "performance", "reservation")
