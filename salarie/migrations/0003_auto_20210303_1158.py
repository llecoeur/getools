# Generated by Django 3.1.6 on 2021-03-03 10:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('activite', '0053_auto_20210226_0934'),
        ('salarie', '0002_auto_20210226_1226'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calendriersalarie',
            name='salarie',
            field=models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='calendrier', to='activite.salarie'),
        ),
    ]