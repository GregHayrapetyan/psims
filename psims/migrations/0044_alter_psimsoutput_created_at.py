# Generated by Django 3.2.3 on 2021-07-23 07:16

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('psims', '0043_auto_20210723_1114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='psimsoutput',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
