# Generated by Django 4.1 on 2022-09-02 08:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('conge', '0017_demandeconge_conge_invalid'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='demandeconge',
            options={'permissions': [('can_validate_conges', 'Peut valider les congés'), ('can_view_conges', 'Peut voir les congés')]},
        ),
    ]