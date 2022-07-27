# Generated by Django 3.2.3 on 2021-10-27 11:56

import django.core.validators
from django.db import migrations, models
import psims.models


class Migration(migrations.Migration):

    dependencies = [
        ('psims', '0094_auto_20210920_1320'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='multy_markers',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='plantingparameters',
            name='planting_date',
            field=psims.models.PsimsIntegerField(default=None, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(366)]),
        ),
    ]