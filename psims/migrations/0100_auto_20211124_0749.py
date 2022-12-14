# Generated by Django 3.2.9 on 2021-11-24 07:49

from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('psims', '0099_alter_plantingparameters_plplp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='company',
            field=models.CharField(default='', max_length=30),
        ),
        migrations.AlterField(
            model_name='profile',
            name='crops_regions',
            field=models.CharField(blank=True, default='', max_length=30),
        ),
        migrations.AlterField(
            model_name='profile',
            name='phone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, default='', max_length=128, region=None),
        ),
        migrations.AlterField(
            model_name='profile',
            name='title',
            field=models.CharField(blank=True, default='', max_length=30),
        ),
    ]
