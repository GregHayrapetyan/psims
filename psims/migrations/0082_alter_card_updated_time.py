# Generated by Django 3.2.3 on 2021-09-04 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('psims', '0081_auto_20210904_1151'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='updated_time',
            field=models.DateTimeField(auto_now=True, verbose_name='date_published'),
        ),
    ]
