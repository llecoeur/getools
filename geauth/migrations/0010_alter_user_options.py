# Generated by Django 3.2 on 2021-07-07 10:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('geauth', '0009_auto_20210526_1225'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'permissions': [('can_view_indicators', 'Peut voir les indicateurs')], 'verbose_name': 'user', 'verbose_name_plural': 'users'},
        ),
    ]
