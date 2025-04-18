# Generated by Django 5.2 on 2025-04-10 13:33

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0031_alter_tag_detail_alter_tag_type_alter_tag_value'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='tag',
            name='tag_unique_on_value_type_and_user',
        ),
        migrations.AddConstraint(
            model_name='tag',
            constraint=models.UniqueConstraint(fields=('value', 'type', 'user'), name='tag_unique_on_value_type_and_user', nulls_distinct=False),
        ),
    ]
