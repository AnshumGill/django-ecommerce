# Generated by Django 2.1.3 on 2018-12-13 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_auto_20181213_1148'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='slug',
            field=models.SlugField(default='abc'),
            preserve_default=False,
        ),
    ]
