# Generated by Django 4.0 on 2024-10-18 16:24

from django.db import migrations, models
import localized_fields.fields.char_field


class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0002_alter_teacher_last_name'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserQuestion',
        ),
        migrations.AlterModelOptions(
            name='teacher',
            options={'verbose_name': 'Учитель', 'verbose_name_plural': 'Учители'},
        ),
        migrations.AddField(
            model_name='teacher',
            name='subject_name',
            field=localized_fields.fields.char_field.LocalizedCharField(null=True, required=['ru'], verbose_name='Название предмета'),
        ),
        migrations.AddField(
            model_name='userrequest',
            name='request_type',
            field=models.CharField(choices=[('question', 'Вопрос'), ('request', 'Заявка')], default='question', max_length=100, verbose_name='Тип запроса'),
        ),
        migrations.AddField(
            model_name='userrequest',
            name='text',
            field=models.TextField(blank=True, null=True, verbose_name='Вопрос'),
        ),
    ]
