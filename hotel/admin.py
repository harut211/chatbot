from django.contrib import admin

from .models import Reservation, Room

admin.site.site_header = "Հյուրանոցի կառավարման վահանակ"
admin.site.site_title = "Ադմինիստրատորի վահանակ"
admin.site.index_title = "Կառավարում"


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("room_number", "room_type", "capacity", "price_per_night", "is_available")
    list_filter = ("room_type", "capacity", "is_available")
    search_fields = ("room_number", "room_type")


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("guest_name", "room", "check_in_date", "nights", "total_price", "created_at")
    list_filter = ("check_in_date", "room__room_type")
    search_fields = ("guest_name", "room__room_number")
