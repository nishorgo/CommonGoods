# Generated by Django 5.0.1 on 2024-01-29 14:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_productshop_updated_at'),
    ]

    operations = [
        migrations.RenameField(
            model_name='business',
            old_name='sheet_ID',
            new_name='sheet_id',
        ),
    ]
