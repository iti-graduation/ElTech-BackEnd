# Generated by Django 4.2.7 on 2023-11-21 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_order_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='address',
            field=models.CharField(default='', max_length=255),
        ),
    ]