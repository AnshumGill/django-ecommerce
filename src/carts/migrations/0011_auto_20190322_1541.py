# Generated by Django 2.1.3 on 2019-03-22 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0010_auto_20190322_1338'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='products',
            field=models.TextField(default=dict),
        ),
    ]
