# Generated by Django 3.0.7 on 2020-06-26 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activite', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='rubriquepaie',
            name='abrege',
            field=models.CharField(default='', max_length=70, verbose_name='Abrégé'),
        ),
    ]
