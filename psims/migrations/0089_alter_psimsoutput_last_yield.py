# Generated by Django 3.2.3 on 2021-09-13 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('psims', '0088_alter_psimsoutput_last_yield'),
    ]

    operations = [
        migrations.AlterField(
            model_name='psimsoutput',
            name='last_yield',
            field=models.IntegerField(null=True),
        ),
    ]
