# Generated by Django 5.0.1 on 2024-02-05 06:37

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_rename_bin_business_bin_no'),
    ]

    operations = [
        migrations.RenameField(
            model_name='business',
            old_name='rating',
            new_name='business_rating',
        ),
        migrations.AddField(
            model_name='business',
            name='captcha_score',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='business',
            name='country',
            field=models.CharField(blank=True, max_length=40, null=True, verbose_name='Country'),
        ),
        migrations.AddField(
            model_name='business',
            name='county',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='County/Province/State'),
        ),
        migrations.AddField(
            model_name='business',
            name='has_profile',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='business',
            name='post_code',
            field=models.CharField(blank=True, max_length=8, null=True, verbose_name='Post Code'),
        ),
        migrations.AddField(
            model_name='business',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='business',
            name='town',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Town/City'),
        ),
        migrations.AddField(
            model_name='business',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='business',
            name='address',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Address'),
        ),
        migrations.AlterField(
            model_name='business',
            name='contact',
            field=models.CharField(max_length=11),
        ),
        migrations.AlterField(
            model_name='business',
            name='latitude',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Latitude'),
        ),
        migrations.AlterField(
            model_name='business',
            name='longitude',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Longitude'),
        ),
    ]
