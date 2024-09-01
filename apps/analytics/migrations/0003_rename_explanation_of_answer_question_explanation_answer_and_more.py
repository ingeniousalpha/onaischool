# Generated by Django 4.0 on 2024-08-15 19:33

from django.db import migrations
import localized_fields.fields.file_field


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0002_question_explanation_of_answer'),
    ]

    operations = [
        migrations.RenameField(
            model_name='question',
            old_name='explanation_of_answer',
            new_name='explanation_answer',
        ),
        migrations.AddField(
            model_name='question',
            name='explanation_answer_image',
            field=localized_fields.fields.file_field.LocalizedFileField(blank=True, null=True, required=[], upload_to='images/analytics/', verbose_name='Объяснение ответа(видео)'),
        ),
    ]