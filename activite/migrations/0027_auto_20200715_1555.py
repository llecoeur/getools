# Generated by Django 3.0.7 on 2020-07-15 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activite', '0026_remove_tarifge_salarie'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adherent',
            name='code_erp',
            field=models.CharField(blank=True, db_index=True, default=None, max_length=200, null=True, verbose_name='Code ERP'),
        ),
        migrations.AlterField(
            model_name='article',
            name='code_erp',
            field=models.CharField(blank=True, db_index=True, default='', max_length=200, null=True, verbose_name='Code ERP'),
        ),
        migrations.AlterField(
            model_name='article',
            name='libelle',
            field=models.CharField(db_index=True, max_length=70, verbose_name='Libelle'),
        ),
        migrations.AlterField(
            model_name='article',
            name='type_article',
            field=models.CharField(db_index=True, default='', max_length=70, verbose_name='Type'),
        ),
        migrations.AlterField(
            model_name='famillearticle',
            name='code_erp',
            field=models.CharField(blank=True, db_index=True, default='', max_length=200, null=True, verbose_name='Code ERP'),
        ),
        migrations.AlterField(
            model_name='famillearticle',
            name='forfaitaire',
            field=models.BooleanField(db_index=True, default=False, verbose_name='Forfaitaire'),
        ),
        migrations.AlterField(
            model_name='famillearticle',
            name='libelle',
            field=models.CharField(db_index=True, max_length=70, verbose_name='Libelle'),
        ),
        migrations.AlterField(
            model_name='miseadisposition',
            name='cloturee',
            field=models.BooleanField(db_index=True, default=False, verbose_name='Mise à disposition cloturée ?'),
        ),
        migrations.AlterField(
            model_name='miseadisposition',
            name='code_erp',
            field=models.CharField(db_index=True, max_length=18, verbose_name='Code ERP'),
        ),
        migrations.AlterField(
            model_name='poste',
            name='code_erp',
            field=models.CharField(blank=True, db_index=True, default=None, max_length=70, null=True, verbose_name='Code ERP'),
        ),
        migrations.AlterField(
            model_name='rubriquepaie',
            name='code_erp',
            field=models.CharField(blank=True, db_index=True, default=None, max_length=70, null=True, verbose_name='Code ERP'),
        ),
        migrations.AlterField(
            model_name='salarie',
            name='code_erp',
            field=models.CharField(blank=True, db_index=True, default=None, max_length=200, null=True, verbose_name='Code ERP'),
        ),
        migrations.AlterField(
            model_name='salarie',
            name='date_entree',
            field=models.DateField(blank=True, db_index=True, default=None, null=True, verbose_name="Date d'entrée"),
        ),
        migrations.AlterField(
            model_name='salarie',
            name='date_sortie',
            field=models.DateField(blank=True, db_index=True, default=None, null=True, verbose_name='Date de sortie'),
        ),
        migrations.AlterField(
            model_name='service',
            name='code_erp',
            field=models.CharField(blank=True, db_index=True, default=None, max_length=70, null=True, verbose_name='Code ERP'),
        ),
        migrations.AlterField(
            model_name='tarifge',
            name='code_erp',
            field=models.IntegerField(db_index=True, default=0),
        ),
    ]