# Generated by Django 5.2 on 2025-04-09 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0022_artistrequest_beatport_artist_id_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='artist',
            name='beatport_artist_id_if_set_unique',
        ),
        migrations.RemoveConstraint(
            model_name='genre',
            name='beatport_genre_id_if_set_unique',
        ),
        migrations.RemoveConstraint(
            model_name='label',
            name='beatport_label_id_if_set_unique',
        ),
        migrations.RemoveConstraint(
            model_name='track',
            name='beatport_track_id_if_set_unique',
        ),
        migrations.AddConstraint(
            model_name='artist',
            constraint=models.UniqueConstraint(condition=models.Q(('beatport_artist_id__isnull', False)), fields=('beatport_artist_id',), name='beatport_artist_id_if_set_unique', violation_error_message='This artist ID from Beatport is already attached to another artist.'),
        ),
        migrations.AddConstraint(
            model_name='genre',
            constraint=models.UniqueConstraint(condition=models.Q(('beatport_genre_id__isnull', False)), fields=('beatport_genre_id',), name='beatport_genre_id_if_set_unique', violation_error_message='This genre ID from Beatport is already attached to another genre.'),
        ),
        migrations.AddConstraint(
            model_name='label',
            constraint=models.UniqueConstraint(condition=models.Q(('beatport_label_id__isnull', False)), fields=('beatport_label_id',), name='beatport_label_id_if_set_unique', violation_error_message='This label ID from Beatport is already attached to another label.'),
        ),
        migrations.AddConstraint(
            model_name='track',
            constraint=models.UniqueConstraint(condition=models.Q(('beatport_track_id__isnull', False)), fields=('beatport_track_id',), name='beatport_track_id_if_set_unique', violation_error_message='This track ID from Beatport is already attached to another track.'),
        ),
    ]
