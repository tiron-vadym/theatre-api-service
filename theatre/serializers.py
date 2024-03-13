from django.db import transaction
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


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ("id", "first_name", "last_name")


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("id", "name")


class PlaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Play
        fields = (
            "id",
            "title",
            "description",
            "actors",
            "genres",
            "image"
        )


class PlayListSerializer(PlaySerializer):
    class Meta:
        model = Play
        fields = (
            "id",
            "title",
            "description",
            "actor_count",
            "image"
        )


class PlayDetailSerializer(PlaySerializer):
    class Meta:
        model = Play
        fields = (
            "id",
            "title",
            "description",
            "actors",
            "genres",
            "image"
        )


class PlayImageSerializer(PlaySerializer):
    class Meta:
        model = Play
        fields = ("id", "image")


class TheatreHallSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheatreHall
        fields = ("id", "name", "rows", "seats_in_row")


class PerformanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Performance
        fields = ("id", "play", "theatre_hall", "show_time")


class PerformanceListSerializer(PerformanceSerializer):
    play = serializers.CharField(source="play.title", read_only=True)
    theatre_hall = serializers.CharField(source="theatre_hall.name", read_only=True)
    seats_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Performance
        fields = ("id", "play", "theatre_hall", "show_time", "seats_available")


class PerformanceDetailSerializer(PerformanceSerializer):
    play = PlaySerializer(many=False, read_only=True)
    theatre_hall = TheatreHallSerializer(many=False, read_only=True)
    taken_seats = serializers.SerializerMethodField()

    class Meta:
        model = Performance
        fields = ("id", "play", "theatre_hall", "show_time", "taken_seats")

    def get_taken_seats(self, obj):
        return Ticket.objects.filter(performance=obj).values_list(
            "row",
            "seat"
        )


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs)
        Ticket.validate_seat(
            attrs["seat"],
            attrs["performance"].theatre_hall.seats_in_row,
            serializers.ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "performance", "reservation")


class TicketListSerializer(serializers.ModelSerializer):
    performance = PerformanceListSerializer(many=False, read_only=True)
    owner = serializers.CharField(source="reservation.user", read_only=True)

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "performance", "owner")


class ReservationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reservation
        fields = ("id", "user", "created_at")


class ReservationListSerializer(ReservationSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)

    class Meta:
        model = Reservation
        fields = ("id", "tickets", "created_at")


class TicketDetailSerializer(TicketSerializer):
    performance = PerformanceDetailSerializer(many=False, read_only=True)
    reservation = ReservationSerializer(many=False, read_only=True)

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "performance", "reservation")
