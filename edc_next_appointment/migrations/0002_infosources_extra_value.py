# Generated by Django 4.2.3 on 2023-08-02 23:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("edc_next_appointment", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="infosources",
            name="extra_value",
            field=models.CharField(max_length=250, null=True),
        ),
    ]
