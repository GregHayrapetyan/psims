# Generated by Django 3.2.3 on 2021-07-06 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('psims', '0018_auto_20210706_1321'),
    ]

    operations = [
        migrations.AlterField(
            model_name='psimsoutput',
            name='weighted_index',
            field=models.IntegerField(null=True),
        ),
    ]
