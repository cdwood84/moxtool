# Generated by Django 5.1.6 on 2025-03-13 19:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='artist',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='genre',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='playlist',
            options={'ordering': ['date_added'], 'permissions': (('can_view_public_playlist', 'Browse public playlists'),)},
        ),
        migrations.AlterModelOptions(
            name='tag',
            options={'ordering': ['type', 'date_added'], 'permissions': (('can_view_public_tag', 'Browse public tags'),)},
        ),
        migrations.AlterModelOptions(
            name='track',
            options={'ordering': ['title']},
        ),
        migrations.AlterModelOptions(
            name='trackinstance',
            options={'ordering': ['date_added'], 'permissions': (('can_view_public_trackinstance', 'Browse public tracks'),)},
        ),
    ]
