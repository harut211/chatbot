from django.contrib import admin
from django.utils.html import format_html

from .models import Reservation, Room

admin.site.site_header = "Հյուրանոցի կառավարման վահանակ"
admin.site.site_title = "Ադմինիստրատորի վահանակ"
admin.site.index_title = "Կառավարում"


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = (
        "room_number",
        "room_type",
        "capacity",
        "price_per_night",
        "is_available",
        "image_thumb",
    )
    list_filter = ("room_type", "capacity", "is_available")
    search_fields = ("room_number", "room_type")
    readonly_fields = ("image_preview",)
    fieldsets = (
        (None, {
            "fields": (
                "room_number",
                "room_type",
                "capacity",
                "price_per_night",
                "is_available",
                "image",
                "image_preview",
            )
        }),
    )

    def image_thumb(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 80px; height: 60px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url,
            )
        return "-"
    image_thumb.short_description = "Լուսանկար"

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 320px; height: auto; object-fit: cover; border-radius: 6px;" />',
                obj.image.url,
            )
        return "Չկա լուսանկար"
    image_preview.short_description = "Նախադիտում"


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("guest_name", "room", "check_in_date", "nights", "total_price", "created_at")
    list_filter = ("check_in_date", "room__room_type")
    search_fields = ("guest_name", "room__room_number")
