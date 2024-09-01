# Generated by Django 4.0 on 2024-08-15 20:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0003_rename_explanation_of_answer_question_explanation_answer_and_more'),
        ('users', '0006_user_full_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserQuizQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Время создания')),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True, verbose_name='Время последнего изменения')),
                ('is_correct', models.BooleanField(blank=True, null=True)),
                ('answer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_quiz_questions', to='analytics.answeroption')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_quiz_questions', to='analytics.question')),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_quiz_questions', to='analytics.quiz')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_quiz_questions', to='users.user', verbose_name='Пользователь')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]