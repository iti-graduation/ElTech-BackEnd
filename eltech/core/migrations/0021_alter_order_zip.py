# Generated by Django 4.2.7 on 2023-11-21 16:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_alter_order_address_alter_order_country_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='zip',
            field=models.IntegerField(null=True),
        ),
    ]
