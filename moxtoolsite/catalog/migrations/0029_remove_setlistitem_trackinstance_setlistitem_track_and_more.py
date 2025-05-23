# Generated by Django 5.2 on 2025-04-10 00:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0028_remove_trackinstance_user_track_unique_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='setlistitem',
            name='trackinstance',
        ),
        migrations.AddField(
            model_name='setlistitem',
            name='track',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, to='catalog.track'),
        ),
        migrations.AlterField(
            model_name='playlist',
            name='track',
            field=models.ManyToManyField(help_text='Select one or more tracks for this playlist.', to='catalog.track', verbose_name='tracks'),
        ),
        migrations.AlterField(
            model_name='transition',
            name='from_track',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='from_track', to='catalog.track'),
        ),
        migrations.AlterField(
            model_name='transition',
            name='to_track',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='to_track', to='catalog.track'),
        ),
    ]
