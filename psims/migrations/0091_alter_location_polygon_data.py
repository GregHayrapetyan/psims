# Generated by Django 3.2.3 on 2021-09-17 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('psims', '0090_alter_psimsoutput_last_yield'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='polygon_data',
            field=models.TextField(blank=True, null=True),
        ),
    ]
