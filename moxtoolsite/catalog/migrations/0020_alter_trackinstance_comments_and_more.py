# Generated by Django 5.2 on 2025-04-08 13:53

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0019_label_setlist_setlistitem_transition_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='trackinstance',
            name='comments',
            field=models.TextField(help_text='Enter any notes you want to remember about this track.', max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='trackinstance',
            name='date_added',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='trackinstance',
            name='rating',
            field=models.CharField(choices=[('0', 'unplayable'), ('1', 'atrocious'), ('2', 'terrible'), ('3', 'bad'), ('4', 'meh'), ('5', 'okay'), ('6', 'fine'), ('7', 'good'), ('8', 'great'), ('9', 'excellent'), ('10', 'perfect')], default=None, help_text='Track rating', max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='trackinstance',
            name='track',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='catalog.track'),
        ),
        migrations.AlterField(
            model_name='trackinstance',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
