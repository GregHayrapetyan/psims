# Generated by Django 3.2.3 on 2021-07-12 08:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('psims', '0022_auto_20210709_1716'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='psimsoutput',
            name='is_open',
        ),
    ]
