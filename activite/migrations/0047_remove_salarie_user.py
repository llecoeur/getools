# Generated by Django 3.1.3 on 2020-11-05 14:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activite', '0046_auto_20201105_1551'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='salarie',
            name='user',
        ),
    ]