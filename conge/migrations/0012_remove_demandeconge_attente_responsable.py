# Generated by Django 3.2 on 2022-03-04 15:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('conge', '0011_alter_demandeconge_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='demandeconge',
            name='attente_responsable',
        ),
    ]
