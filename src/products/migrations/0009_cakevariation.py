# Generated by Django 2.1.3 on 2019-03-16 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_auto_20181213_2155'),
    ]

    operations = [
        migrations.CreateModel(
            name='CakeVariation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.CharField(choices=[('0.5', '½ kg'), ('1', '1 kg'), ('1.5', '1½ kg'), ('2', '2 kg'), ('2.5', '2½ kg'), ('3', '3 kg')], max_length=20)),
                ('quantity', models.CharField(choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10')], max_length=2)),
            ],
        ),
    ]
