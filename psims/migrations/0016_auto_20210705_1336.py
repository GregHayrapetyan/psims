# Generated by Django 3.2.3 on 2021-07-05 09:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('psims', '0015_psimsoutput_is_open'),
    ]

    operations = [
        migrations.CreateModel(
            name='Weather',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='unnamed weather', max_length=20)),
                ('description', models.CharField(default='generic description', max_length=2000)),
            ],
        ),
        migrations.AddField(
            model_name='psimsoutput',
            name='weighted_index',
            field=models.IntegerField(null=True),
        ),
    ]
