# Generated by Django 5.1.6 on 2025-03-14 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0007_alter_track_artist'),
    ]

    operations = [
        migrations.AlterField(
            model_name='track',
            name='artist',
            field=models.ManyToManyField(help_text='Select an artist for this track', to='catalog.artist'),
        ),
    ]
