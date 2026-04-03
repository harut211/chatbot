from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("hotel", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Reservation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("guest_name", models.CharField(max_length=100)),
                ("check_in_date", models.DateField()),
                ("nights", models.PositiveIntegerField(default=1)),
                ("total_price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "room",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="reservations", to="hotel.room"),
                ),
            ],
        ),
    ]
