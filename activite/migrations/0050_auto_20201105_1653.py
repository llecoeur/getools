# Generated by Django 3.1.3 on 2020-11-05 15:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activite', '0049_remove_salarie_user'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='salarie',
            options={'ordering': ['nom']},
        ),
    ]
