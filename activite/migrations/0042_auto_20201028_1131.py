# Generated by Django 3.1.2 on 2020-10-28 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activite', '0041_auto_20201028_1041'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tarifge',
            name='tarif',
            field=models.FloatField(db_index=True, default=0, verbose_name='Montant'),
        ),
    ]
