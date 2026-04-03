from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Room",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("room_number", models.CharField(max_length=20, unique=True)),
                ("room_type", models.CharField(max_length=50)),
                ("price_per_night", models.DecimalField(decimal_places=2, max_digits=10)),
                ("is_available", models.BooleanField(default=True)),
            ],
        ),
    ]
