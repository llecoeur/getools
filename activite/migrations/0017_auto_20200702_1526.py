# Generated by Django 3.0.7 on 2020-07-02 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activite', '0016_auto_20200702_1332'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='affaire',
            name='heures_mensuelles',
        ),
        migrations.RemoveField(
            model_name='affaire',
            name='heures_quotidiennes',
        ),
        migrations.AddField(
            model_name='affaire',
            name='duree_travail_mensuel',
            field=models.FloatField(default=0, verbose_name='Temps de travail mensuel'),
        ),
        migrations.AddField(
            model_name='affaire',
            name='duree_travail_quotidien',
            field=models.FloatField(default=0, verbose_name='Temps de travail quotidien'),
        ),
        migrations.AlterField(
            model_name='affaire',
            name='cloturee',
            field=models.BooleanField(default=False, verbose_name='Affaire cloturée ?'),
        ),
    ]