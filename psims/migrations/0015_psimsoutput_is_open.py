# Generated by Django 3.2.3 on 2021-07-01 07:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('psims', '0014_auto_20210630_1808'),
    ]

    operations = [
        migrations.AddField(
            model_name='psimsoutput',
            name='is_open',
            field=models.BooleanField(default=False),
        ),
    ]
