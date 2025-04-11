# Generated by Django 5.2 on 2025-04-11 17:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0036_alter_transition_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='setlistitem',
            name='track',
            field=models.ForeignKey(help_text='Select a track for this setlist.', null=True, on_delete=django.db.models.deletion.RESTRICT, to='catalog.track'),
        ),
    ]
