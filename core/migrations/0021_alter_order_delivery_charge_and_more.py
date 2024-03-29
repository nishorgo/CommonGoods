# Generated by Django 5.0.2 on 2024-02-27 16:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_order_delivery_charge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='delivery_charge',
            field=models.DecimalField(decimal_places=2, max_digits=6, null=True),
        ),
        migrations.AlterField(
            model_name='productshop',
            name='platform_price',
            field=models.DecimalField(decimal_places=2, max_digits=6),
        ),
        migrations.AlterField(
            model_name='productshop',
            name='retail_price',
            field=models.DecimalField(decimal_places=2, max_digits=6),
        ),
    ]
