# Generated by Django 3.2 on 2021-10-29 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conge', '0003_auto_20211020_1424'),
    ]

    operations = [
        migrations.AddField(
            model_name='validationadherent',
            name='slug_acceptation',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='Sulg de Validation'),
        ),
        migrations.AddField(
            model_name='validationadherent',
            name='slug_refus',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='Sulg de Validation'),
        ),
    ]
