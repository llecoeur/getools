# Generated by Django 3.0.7 on 2020-07-24 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activite', '0029_article_ordre'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tarifge',
            name='mode_calcul',
            field=models.IntegerField(blank=True, default=None, null=True, verbose_name='Mode de Calcul'),
        ),
    ]