# Generated by Django 3.1.3 on 2020-12-10 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('releve', '0012_auto_20201210_0956'),
    ]

    operations = [
        migrations.AlterField(
            model_name='relevesalarie',
            name='commentaire',
            field=models.TextField(blank=True, default='', verbose_name='Commentaires'),
        ),
    ]
