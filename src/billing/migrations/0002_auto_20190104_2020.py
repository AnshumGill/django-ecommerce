# Generated by Django 2.1.3 on 2019-01-04 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='billingprofile',
            name='customer_id',
            field=models.CharField(blank=True, max_length=120, null=True),
        ),
        migrations.AddField(
            model_name='billingprofile',
            name='email',
            field=models.EmailField(default='abc123@gmail.com', max_length=254),
            preserve_default=False,
        ),
    ]
