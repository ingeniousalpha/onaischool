# Generated by Django 4.0 on 2024-08-27 19:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0009_alter_chapter_quarter'),
    ]

    operations = [
        migrations.AddField(
            model_name='direction',
            name='enable_all',
            field=models.BooleanField(default=False),
        ),
    ]
