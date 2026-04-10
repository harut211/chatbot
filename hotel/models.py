from django.db import models


class Room(models.Model):
    room_number = models.CharField("Սենյակի համար", max_length=20, unique=True)
    room_type = models.CharField("Սենյակի տեսակ", max_length=50)
    capacity = models.PositiveIntegerField("Տարողություն", default=2)
    price_per_night = models.DecimalField("Գին մեկ գիշերվա համար", max_digits=10, decimal_places=2)
    is_available = models.BooleanField("Հասանելի է", default=True)

    def __str__(self):
        return f"Room {self.room_number} ({self.room_type})"

    class Meta:
        verbose_name = "Սենյակ"
        verbose_name_plural = "Սենյակներ"


class Reservation(models.Model):
    room = models.ForeignKey(Room, verbose_name="Սենյակ", on_delete=models.PROTECT, related_name="reservations")
    guest_name = models.CharField("Հյուրի անուն", max_length=100)
    check_in_date = models.DateField("Մուտքի ամսաթիվ")
    nights = models.PositiveIntegerField("Գիշերների քանակ", default=1)
    total_price = models.DecimalField("Ընդհանուր արժեք", max_digits=10, decimal_places=2)
    created_at = models.DateTimeField("Ստեղծման ամսաթիվ", auto_now_add=True)

    def __str__(self):
        return f"Reservation for {self.guest_name} in room {self.room.room_number}"

    class Meta:
        verbose_name = "Ամրագրում"
        verbose_name_plural = "Ամրագրումներ"
