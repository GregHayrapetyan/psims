# Generated by Django 3.2.3 on 2021-06-27 11:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('psims', '0009_auto_20210626_1809'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='location',
            name='out',
        ),
    ]
