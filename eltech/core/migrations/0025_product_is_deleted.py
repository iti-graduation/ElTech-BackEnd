# Generated by Django 4.2.7 on 2023-11-22 21:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_merge_20231122_1752'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
