from rest_framework.viewsets import GenericViewSet
from rest_framework.authentication import TokenAuthentication

from .models import (
    Play,
    Actor,
    Genre,
    TheatreHall,
    Performance,
    Reservation,
    Ticket,
)
from .serializers import (
    PlaySerializer,
    PlayListSerializer,
    PlayDetailSerializer,
    ActorSerializer,
    GenreSerializer,
    TheatreHallSerializer,
    PerformanceSerializer,
    ReservationSerializer,
    TicketSerializer,
    TicketListSerializer,
    TicketDetailSerializer,
)
from .permissions import IsAdminOrIfAuthenticatedReadOnly


class PlayViewSet(GenericViewSet):
    queryset = Play.objects.all().prefetch_related("actors", "genres")
    serializer_class = PlaySerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return PlayListSerializer
        if self.action == "retrieve":
            return PlayDetailSerializer
        return PlaySerializer


class ActorViewSet(GenericViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class GenreViewSet(GenericViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class TheatreHallViewSet(GenericViewSet):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class PerformanceViewSet(GenericViewSet):
    queryset = Performance.objects.all().select_related("play")
    serializer_class = PerformanceSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class ReservationViewSet(GenericViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TicketViewSet(GenericViewSet):
    queryset = Ticket.objects.all().select_related(
        "performance",
        "reservation"
    )
    serializer_class = TicketSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer
        if self.action == "retrieve":
            return TicketDetailSerializer
        return TicketSerializer
