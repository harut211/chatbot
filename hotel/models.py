from django.db import models


class Room(models.Model):
    room_number = models.CharField(max_length=20, unique=True)
    room_type = models.CharField(max_length=50)
    capacity = models.PositiveIntegerField(default=2)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"Room {self.room_number} ({self.room_type})"


class Reservation(models.Model):
    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name="reservations")
    guest_name = models.CharField(max_length=100)
    check_in_date = models.DateField()
    nights = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reservation for {self.guest_name} in room {self.room.room_number}"
