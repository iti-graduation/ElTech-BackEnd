# Generated by Django 4.2.7 on 2023-11-13 02:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_review_product'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='total_price',
        ),
    ]
