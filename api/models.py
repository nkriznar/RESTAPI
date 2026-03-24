import uuid

from django.db import models


class Hotel(models.Model):
    """Stores available hotels."""

    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Reservation(models.Model):
    """
    Stores a hotel reservation with check-in/check-out dates and a
    system-generated UUID confirmation number.
    """

    hotel_name = models.CharField(max_length=255)
    checkin = models.DateField()
    checkout = models.DateField()
    confirmation_number = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )

    class Meta:
        ordering = ["-checkin"]

    def __str__(self):
        return f"{self.hotel_name} — {self.confirmation_number}"


class Guest(models.Model):
    """
    Stores guest details. Each guest is linked to exactly one Reservation
    via a ForeignKey (one reservation can have many guests).
    """

    GENDER_CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
    ]

    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.CASCADE,
        related_name="guests",
    )
    guest_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)

    def __str__(self):
        return self.guest_name
