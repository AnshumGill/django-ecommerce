# Generated by Django 2.1.3 on 2019-03-21 21:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0006_auto_20190322_0228'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='cart',
            name='updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
