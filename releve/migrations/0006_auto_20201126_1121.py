# Generated by Django 3.1.3 on 2020-11-26 10:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('activite', '0050_auto_20201105_1653'),
        ('releve', '0005_saisiesalarie_commentaire'),
    ]

    operations = [
        migrations.AlterField(
            model_name='saisiesalarie',
            name='adherent',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='saisie_salarie_list', to='activite.adherent', verbose_name='Adhérent'),
        ),
    ]
