# Generated by Django 5.1.6 on 2025-03-16 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0008_alter_track_artist'),
    ]

    operations = [
        migrations.AddField(
            model_name='track',
            name='mix',
            field=models.CharField(blank=True, choices=[('o', 'Original Mix'), ('e', 'Extended Mix'), ('x', 'Remix'), ('r', 'Radio Mix')], default=None, help_text='the mix version of the track (e.g. Original Mix, Remix, etc.)', max_length=12, null=True),
        ),
        migrations.AddField(
            model_name='track',
            name='remix_artist',
            field=models.ManyToManyField(blank=True, help_text='Select a remix artist for this track', related_name='remix_artist', to='catalog.artist'),
        ),
    ]
