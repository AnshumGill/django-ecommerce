# Generated by Django 2.1.3 on 2019-03-22 11:20

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0018_auto_20190322_1645'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='variations',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True),
        ),
    ]
