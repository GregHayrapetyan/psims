# Generated by Django 3.2.3 on 2021-08-02 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('psims', '0051_psimsoutput_last_step_json'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('price', models.IntegerField(default=0)),
            ],
        ),
    ]
