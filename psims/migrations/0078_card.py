# Generated by Django 3.2.3 on 2021-09-03 08:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('psims', '0077_profile_is_paid'),
    ]

    operations = [
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('number', models.FloatField()),
                ('value', models.CharField(max_length=30)),
                ('desctiption', models.CharField(max_length=100)),
            ],
        ),
    ]
