# Generated by Django 3.2.3 on 2021-07-30 15:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('psims', '0049_psimsoutput_last_step_json'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='psimsoutput',
            name='last_step_json',
        ),
    ]