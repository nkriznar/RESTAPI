from django.db.models import Q
from rest_framework import generics, status
from rest_framework.response import Response

from .models import Hotel, Reservation
from .serializers import HotelSerializer, ReservationSerializer


class HotelListView(generics.ListAPIView):
    """
    GET /api/hotels/?checkin=YYYY-MM-DD&checkout=YYYY-MM-DD

    Returns all hotels. When checkin and checkout query parameters are
    provided, hotels that already have a reservation overlapping the
    requested date range are excluded.
    """

    serializer_class = HotelSerializer

    def get_queryset(self):
        queryset = Hotel.objects.all()
        checkin = self.request.query_params.get("checkin")
        checkout = self.request.query_params.get("checkout")

        if checkin and checkout:
            # Find hotels whose names appear in overlapping reservations.
            # Two date ranges overlap when: start_a < end_b AND start_b < end_a
            overlapping_hotel_names = Reservation.objects.filter(
                Q(checkin__lt=checkout) & Q(checkout__gt=checkin)
            ).values_list("hotel_name", flat=True)

            queryset = queryset.exclude(name__in=overlapping_hotel_names)

        return queryset


class ReservationCreateView(generics.CreateAPIView):
    """
    POST /api/reservations/

    Accepts nested JSON with hotel_name, checkin, checkout, and
    guests_list. Returns the auto-generated confirmation_number.
    """

    serializer_class = ReservationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reservation = serializer.save()

        return Response(
            {"confirmation_number": str(reservation.confirmation_number)},
            status=status.HTTP_201_CREATED,
        )
