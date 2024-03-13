from django.db.models import Count, F
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiParameter


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
    PlayImageSerializer,
    ActorSerializer,
    GenreSerializer,
    TheatreHallSerializer,
    PerformanceSerializer,
    PerformanceListSerializer,
    PerformanceDetailSerializer,
    ReservationSerializer,
    ReservationListSerializer,
    TicketSerializer,
    TicketListSerializer,
    TicketDetailSerializer,
)
from .permissions import IsAdminOrIfAuthenticatedReadOnly


class ActorViewSet(ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class GenreViewSet(ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class PlayViewSet(viewsets.ModelViewSet):
    queryset = Play.objects.all()
    serializer_class = PlaySerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = super().get_queryset()
        title = self.request.query_params.get("title")

        if title:
            queryset = queryset.filter(title__icontains=title)

        return queryset.prefetch_related("actors", "genres").distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return PlayListSerializer
        if self.action == "retrieve":
            return PlayDetailSerializer
        if self.action == "upload_image":
            return PlayImageSerializer
        return PlaySerializer

    @action(methods=["POST"], detail=True, url_path="upload-image")
    def upload_image(self, request, pk=None):
        play = self.get_object()
        serializer = self.get_serializer(play, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "title",
                type=str,
                description="title of play",
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class TheatreHallViewSet(ModelViewSet):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class PerformanceViewSet(ModelViewSet):
    queryset = Performance.objects.all()
    serializer_class = PerformanceSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = self.queryset

        if self.action == "list":
            queryset = (
                queryset
                .select_related("play", "theatre_hall")
                .annotate(
                    seats_available=(
                            F("theatre_hall__seats_in_row")
                            - Count("tickets")
                    )
                )
            ).order_by("id")

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PerformanceListSerializer
        if self.action == "retrieve":
            return PerformanceDetailSerializer
        return PerformanceSerializer


class ReservationPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 100


class ReservationViewSet(ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
    pagination_class = ReservationPagination

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        if self.action == "list":
            queryset = queryset.select_related(
                "user",
            ).prefetch_related(
                "tickets__performance"
            )

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return ReservationListSerializer
        return ReservationSerializer


class TicketViewSet(ModelViewSet):
    queryset = Ticket.objects.all().select_related(
        "performance",
        "reservation"
    )
    serializer_class = TicketSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer
        if self.action == "retrieve":
            return TicketDetailSerializer
        return TicketSerializer
