# Generated by Django 3.1.6 on 2021-03-11 16:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('salarie', '0008_auto_20210311_1706'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calendriersalariemiseadisposition',
            name='recurence',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='salarie.calendriersalarierecurence'),
        ),
    ]
