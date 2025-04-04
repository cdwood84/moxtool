# Generated by Django 5.1.6 on 2025-04-04 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0017_alter_playlist_tag_alter_playlist_track_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='track',
            name='mix',
            field=models.CharField(blank=True, choices=[('o', 'Original Mix'), ('e', 'Extended Mix'), ('x', 'Remix'), ('r', 'Radio Mix'), ('i', 'Instrumental Mix')], default=None, help_text='the mix version of the track (e.g. Original Mix, Remix, etc.)', max_length=16, null=True),
        ),
        migrations.AlterField(
            model_name='trackinstance',
            name='comments',
            field=models.TextField(help_text='Enter any notes you want to remember about this track.', max_length=1000),
        ),
        migrations.AlterField(
            model_name='trackinstance',
            name='tag',
            field=models.ManyToManyField(blank=True, help_text='Select one or more tags for this playlist.', to='catalog.tag', verbose_name='tags'),
        ),
        migrations.AlterField(
            model_name='trackrequest',
            name='mix',
            field=models.CharField(blank=True, choices=[('o', 'Original Mix'), ('e', 'Extended Mix'), ('x', 'Remix'), ('r', 'Radio Mix'), ('i', 'Instrumental Mix')], default=None, help_text='the mix version of the track (e.g. Original Mix, Remix, etc.)', max_length=16, null=True),
        ),
    ]
