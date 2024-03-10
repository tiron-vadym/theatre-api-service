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


class PlaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Play
        fields = (
            "id",
            "title",
            "description",
            "actors",
            "genres",
            "actor_count"
        )


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


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs)
        Ticket.validate_seat(
            attrs["seat"],
            attrs["ticket"].performance.theatre_hall.seats_in_row,
            serializers.ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "performance", "reservation")


class TicketListSerializer(TicketSerializer):
    performance = PerformanceSerializer(many=False, read_only=True)
    owner = serializers.CharField(source="reservation.user", read_only=True)

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "performance", "owner")


class ReservationSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Reservation
        fields = ("id", "tickets", "created_at")

    @transaction.atomic
    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets")
        reservation = Reservation.objects.create(**validated_data)
        for tickets_data in tickets_data:
            Ticket.objects.create(reservation=reservation, **tickets_data)
        return reservation


class TicketDetailSerializer(TicketSerializer):
    performance = PerformanceSerializer(many=False, read_only=True)
    reservation = ReservationSerializer(many=False, read_only=True)

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "performance", "reservation")
