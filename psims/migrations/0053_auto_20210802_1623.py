# Generated by Django 3.2.3 on 2021-08-02 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('psims', '0052_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='product_files/'),
        ),
        migrations.AddField(
            model_name='product',
            name='url',
            field=models.URLField(default=''),
        ),
    ]
