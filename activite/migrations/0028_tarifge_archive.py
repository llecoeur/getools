# Generated by Django 3.0.7 on 2020-07-17 10:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activite', '0027_auto_20200715_1555'),
    ]

    operations = [
        migrations.AddField(
            model_name='tarifge',
            name='archive',
            field=models.BooleanField(default=False, verbose_name='Archivé'),
        ),
    ]
