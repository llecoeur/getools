# Generated by Django 3.0.7 on 2020-07-01 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activite', '0008_tarifge_code_erp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tarifge',
            name='exportable',
            field=models.BooleanField(default=False, null=True, verbose_name='Exportable ?'),
        ),
    ]
