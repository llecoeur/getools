# Generated by Django 3.0.7 on 2020-10-08 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activite', '0033_auto_20200731_1231'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='unite',
            field=models.CharField(default='', max_length=10, verbose_name='Unité'),
        ),
        migrations.AddField(
            model_name='saisieactivite',
            name='uploaded',
            field=models.BooleanField(default=False, verbose_name='Envoyée'),
        ),
    ]
