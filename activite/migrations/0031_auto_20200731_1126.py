# Generated by Django 3.0.7 on 2020-07-31 09:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('activite', '0030_auto_20200724_1043'),
    ]

    operations = [
        migrations.CreateModel(
            name='InfosSupMoisMad',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('heures_travaillees', models.FloatField(verbose_name='Heures Travaillées')),
                ('heures_mensuelles', models.FloatField(verbose_name='heures mensuelles')),
                ('saisiecomplete', models.BooleanField(verbose_name='Saise Comlète ?')),
                ('mise_a_disposition', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='infos_sup_list', to='activite.MiseADisposition')),
            ],
        ),
        migrations.CreateModel(
            name='InfosSupMoisSalarie',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mois', models.IntegerField(verbose_name='Mois')),
                ('annee', models.IntegerField(verbose_name='Année')),
                ('heures_travaillees', models.FloatField(verbose_name='Heures Travaillées')),
                ('heures_theoriques', models.FloatField(verbose_name='heures Théoriques')),
                ('id_detail', models.IntegerField(verbose_name='')),
                ('salarie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='infos_sup_list', to='activite.Salarie')),
            ],
        ),
        migrations.RemoveField(
            model_name='detailcredittemps',
            name='mise_a_disposition',
        ),
        migrations.AlterModelOptions(
            name='article',
            options={'ordering': ['ordre']},
        ),
        migrations.DeleteModel(
            name='CreditTemps',
        ),
        migrations.DeleteModel(
            name='DetailCreditTemps',
        ),
    ]