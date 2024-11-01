# Generated by Django 4.0 on 2024-10-29 14:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0037_user_chat_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='userexamquestion',
            name='exam_result',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_exam_questions', to='users.userexamresult'),
        ),
    ]