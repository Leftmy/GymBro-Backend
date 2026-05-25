from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("exercises", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="exercise",
            name="description_i18n",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
