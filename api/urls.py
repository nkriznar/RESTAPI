from django.urls import path

from . import views

urlpatterns = [
    path("hotels/", views.HotelListView.as_view(), name="hotel-list"),
    path("reservations/", views.ReservationCreateView.as_view(), name="reservation-create"),
]
