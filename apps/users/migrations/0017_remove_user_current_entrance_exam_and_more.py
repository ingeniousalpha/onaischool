# Generated by Django 4.0 on 2024-09-01 14:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0009_examquestion_score'),
        ('users', '0016_user_current_entrance_exam_user_current_topic'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='current_entrance_exam',
        ),
        migrations.AddField(
            model_name='user',
            name='current_exam_per_day',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='users', to='analytics.entranceexamperday'),
        ),
    ]
