# Generated by Django 3.2.3 on 2021-07-16 14:35

from django.db import migrations
import psims.models


class Migration(migrations.Migration):

    dependencies = [
        ('psims', '0027_psimsoutput_is_weighted_index'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plantingparameters',
            name='plpoe',
            field=psims.models.PsimsIntegerField(default=None),
        ),
        migrations.AlterField(
            model_name='plantingparameters',
            name='plpop',
            field=psims.models.PsimsIntegerField(default=None),
        ),
    ]
