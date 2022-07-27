# Generated by Django 3.2.3 on 2021-07-20 09:12

import django.core.validators
from django.db import migrations
import psims.models


class Migration(migrations.Migration):

    dependencies = [
        ('psims', '0040_alter_fertilizationparameters_fertilizer_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fertilizationparameters',
            name='fertilizer_date',
            field=psims.models.PsimsIntegerField(default=1, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(366)]),
        ),
        migrations.AlterField(
            model_name='plantingparameters',
            name='planting_date',
            field=psims.models.PsimsIntegerField(default=201, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(366)]),
        ),
    ]