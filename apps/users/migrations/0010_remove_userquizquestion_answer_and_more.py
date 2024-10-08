# Generated by Django 4.0 on 2024-08-19 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0007_entranceexamsubject_examansweroption_examquestion_and_more'),
        ('users', '0009_alter_userquizquestion_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userquizquestion',
            name='answer',
        ),
        migrations.AddField(
            model_name='userquizquestion',
            name='answers',
            field=models.ManyToManyField(blank=True, null=True, related_name='user_quiz_questions', to='analytics.AnswerOption'),
        ),
    ]
