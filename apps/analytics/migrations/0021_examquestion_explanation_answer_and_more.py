# Generated by Django 4.0 on 2024-11-11 20:11

from django.db import migrations
import localized_fields.fields.file_field
import localized_fields.fields.text_field


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0020_examquestion_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='examquestion',
            name='explanation_answer',
            field=localized_fields.fields.text_field.LocalizedTextField(blank=True, null=True, required=[], verbose_name='Объяснение ответа'),
        ),
        migrations.AddField(
            model_name='examquestion',
            name='explanation_answer_image',
            field=localized_fields.fields.file_field.LocalizedFileField(blank=True, null=True, required=[], upload_to='images/analytics/', verbose_name='Объяснение ответа(видео)'),
        ),
    ]