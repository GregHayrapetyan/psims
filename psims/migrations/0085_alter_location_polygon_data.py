# Generated by Django 3.2.3 on 2021-09-10 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('psims', '0084_location_polygon_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='polygon_data',
            field=models.JSONField(blank=True, default='Not selected area', null=True),
        ),
    ]
