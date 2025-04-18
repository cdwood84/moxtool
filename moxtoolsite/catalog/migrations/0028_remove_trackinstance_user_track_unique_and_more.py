# Generated by Django 5.2 on 2025-04-10 00:01

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0027_alter_genrerequest_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='trackinstance',
            name='user_track_unique',
        ),
        migrations.RemoveConstraint(
            model_name='transition',
            name='fields_not_equal',
        ),
        migrations.RemoveConstraint(
            model_name='transition',
            name='unique_title_subtitle_user',
        ),
        migrations.AlterField(
            model_name='trackrequest',
            name='beatport_track_id',
            field=models.BigIntegerField(help_text='Track ID from Beatport, found in the track URL, which can be used to populate metadata', null=True, verbose_name='Beatport Track ID'),
        ),
        migrations.AlterField(
            model_name='trackrequest',
            name='mix',
            field=models.CharField(help_text='The mix version of the track (e.g. Original Mix, Remix, etc.)', max_length=200, null=True),
        ),
        migrations.AddConstraint(
            model_name='playlist',
            constraint=models.UniqueConstraint(fields=('name', 'user'), name='playlist_unique_on_name_and_user'),
        ),
        migrations.AddConstraint(
            model_name='setlist',
            constraint=models.UniqueConstraint(fields=('name', 'user'), name='setlist_unique_on_name_and_user'),
        ),
        migrations.AddConstraint(
            model_name='setlistitem',
            constraint=models.UniqueConstraint(fields=('setlist', 'start_time'), name='setlistitem_unique_on_setlist_and_start_time'),
        ),
        migrations.AddConstraint(
            model_name='trackinstance',
            constraint=models.UniqueConstraint(fields=('track', 'user'), name='trackinstance_unique_on_track_and_user', violation_error_message='User already has this track in their library'),
        ),
        migrations.AddConstraint(
            model_name='transition',
            constraint=models.CheckConstraint(condition=models.Q(('from_track', models.F('to_track')), _negated=True), name='track_cannot_transition_itself'),
        ),
        migrations.AddConstraint(
            model_name='transition',
            constraint=models.UniqueConstraint(fields=('from_track', 'to_track', 'user'), name='unique_user_track_transition'),
        ),
    ]
