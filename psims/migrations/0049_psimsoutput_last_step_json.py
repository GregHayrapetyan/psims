# Generated by Django 3.2.3 on 2021-07-30 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('psims', '0048_psimsoutput_irrigation_parameters'),
    ]

    operations = [
        migrations.AddField(
            model_name='psimsoutput',
            name='last_step_json',
            field=models.JSONField(null=True),
        ),
    ]