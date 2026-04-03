from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("hotel", "0002_reservation"),
    ]

    operations = [
        migrations.AddField(
            model_name="room",
            name="capacity",
            field=models.PositiveIntegerField(default=2),
        ),
    ]
