# Generated by Django 3.1.3 on 2020-11-05 14:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('activite', '0045_infossupmoissalarie_paie_envoyee'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salarie',
            name='user',
            field=models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='salarie_cegid', to=settings.AUTH_USER_MODEL),
        ),
    ]
