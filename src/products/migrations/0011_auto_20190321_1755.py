# Generated by Django 2.1.3 on 2019-03-21 12:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0010_auto_20190317_2202'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='products',
            name='quantity',
        ),
        migrations.RemoveField(
            model_name='products',
            name='size',
        ),
    ]