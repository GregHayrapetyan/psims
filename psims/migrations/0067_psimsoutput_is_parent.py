# Generated by Django 3.2.3 on 2021-08-23 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('psims', '0066_psimsoutput_long_names'),
    ]

    operations = [
        migrations.AddField(
            model_name='psimsoutput',
            name='is_parent',
            field=models.BooleanField(default=False),
        ),
    ]
