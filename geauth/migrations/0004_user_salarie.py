# Generated by Django 3.1.3 on 2020-11-05 14:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('activite', '0047_remove_salarie_user'),
        ('geauth', '0003_auto_20201014_1419'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='salarie',
            field=models.OneToOneField(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user', to='activite.salarie', verbose_name='Salarié'),
        ),
    ]
