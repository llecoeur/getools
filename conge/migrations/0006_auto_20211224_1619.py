# Generated by Django 3.2 on 2021-12-24 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conge', '0005_auto_20211105_1641'),
    ]

    operations = [
        migrations.AlterField(
            model_name='validationadherent',
            name='slug_acceptation',
            field=models.CharField(blank=True, default='', max_length=32, null=True, verbose_name='Slug de Validation'),
        ),
        migrations.AlterField(
            model_name='validationadherent',
            name='slug_refus',
            field=models.CharField(blank=True, default='', max_length=32, null=True, verbose_name='Slug de refus'),
        ),
    ]