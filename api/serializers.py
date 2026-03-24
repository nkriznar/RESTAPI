from rest_framework import serializers

from .models import Guest, Hotel, Reservation


class HotelSerializer(serializers.ModelSerializer):
    """Serializer for the Hotel model — used by GET /api/hotels/."""

    class Meta:
        model = Hotel
        fields = ["id", "name"]


class GuestSerializer(serializers.ModelSerializer):
    """
    Nested serializer for Guest objects.
    Used inside ReservationSerializer to accept a list of guests.
    """

    class Meta:
        model = Guest
        fields = ["guest_name", "gender"]


class ReservationSerializer(serializers.Serializer):
    """
    Handles the nested POST /api/reservations/ request.

    Input JSON
    -----------
    {
        "hotel_name": "string",
        "checkin": "YYYY-MM-DD",
        "checkout": "YYYY-MM-DD",
        "guests_list": [
            { "guest_name": "string", "gender": "string" }
        ]
    }

    Response JSON
    -------------
    { "confirmation_number": "uuid-string" }

    How the custom create() method works
    -------------------------------------
    1. DRF calls ``is_valid()`` which runs the field-level validations
       defined above (hotel_name, checkin, checkout, guests_list).
    2. When the view calls ``serializer.save()``, DRF delegates to the
       ``create()`` method below because no existing instance was passed.
    3. Inside ``create()``:
       a. We pop ``guests_list`` from the validated data so it doesn't
          get passed to the Reservation constructor.
       b. We create the ``Reservation`` row — Django auto-generates the
          UUID ``confirmation_number`` at this point.
       c. We iterate over each guest dict in ``guests_list`` and create
          a ``Guest`` row linked to the new reservation via the FK.
    4. The view then returns ``{"confirmation_number": str(reservation.confirmation_number)}``.
    """

    hotel_name = serializers.CharField(max_length=255)
    checkin = serializers.DateField()
    checkout = serializers.DateField()
    guests_list = GuestSerializer(many=True)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    def validate(self, attrs):
        """Ensure checkout is after checkin."""
        if attrs["checkout"] <= attrs["checkin"]:
            raise serializers.ValidationError(
                "checkout date must be after checkin date."
            )
        return attrs

    # ------------------------------------------------------------------
    # Custom create — handles nested guest creation
    # ------------------------------------------------------------------
    def create(self, validated_data):
        """
        1. Pop the nested guests_list from validated data.
        2. Create the Reservation (UUID confirmation_number auto-generated).
        3. Bulk-create linked Guest rows.
        4. Return the Reservation instance.
        """
        guests_data = validated_data.pop("guests_list")

        reservation = Reservation.objects.create(**validated_data)

        Guest.objects.bulk_create(
            [
                Guest(reservation=reservation, **guest)
                for guest in guests_data
            ]
        )

        return reservation
