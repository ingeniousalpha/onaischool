# Generated by Django 4.0 on 2024-08-30 19:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_remove_mytopic_course_mytopic_topic'),
    ]

    operations = [
        migrations.AddField(
            model_name='mytopic',
            name='is_completed',
            field=models.BooleanField(default=False),
        ),
    ]