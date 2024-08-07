# Generated by Django 4.1.7 on 2024-07-23 21:08

from django.db import migrations, models
import django.db.models.deletion
import localized_fields.fields.char_field
import localized_fields.fields.file_field
import localized_fields.fields.text_field


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Chapter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.PositiveIntegerField(db_index=True, default=0, verbose_name='Приоритет')),
                ('name', localized_fields.fields.char_field.LocalizedCharField(null=True, required=['ru', 'kk', 'en'], verbose_name='Название')),
                ('quarter', models.CharField(choices=[('1', 'Grade 1'), ('2', 'Grade 2'), ('3', 'Grade 3'), ('4', 'Grade 4')], default='1', max_length=10, verbose_name='Четверть')),
            ],
            options={
                'verbose_name': 'Раздел',
                'verbose_name_plural': 'Разделы',
            },
        ),
        migrations.CreateModel(
            name='Direction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.PositiveIntegerField(db_index=True, default=0, verbose_name='Приоритет')),
                ('name', localized_fields.fields.char_field.LocalizedCharField(null=True, required=['ru', 'kk', 'en'], verbose_name='Название')),
                ('description', localized_fields.fields.text_field.LocalizedTextField(null=True, required=['ru', 'kk', 'en'], verbose_name='Описание')),
                ('image', localized_fields.fields.file_field.LocalizedFileField(blank=True, null=True, required=[], upload_to='images/', verbose_name='Картинка')),
            ],
            options={
                'verbose_name': 'Direction',
                'verbose_name_plural': 'Directions',
            },
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.PositiveIntegerField(db_index=True, default=0, verbose_name='Приоритет')),
                ('name', localized_fields.fields.char_field.LocalizedCharField(null=True, required=['ru', 'kk', 'en'], verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Учетная запись',
                'verbose_name_plural': 'Учетная запись',
            },
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.PositiveIntegerField(db_index=True, default=0, verbose_name='Приоритет')),
                ('name', localized_fields.fields.char_field.LocalizedCharField(null=True, required=['ru', 'kk', 'en'], verbose_name='Название')),
                ('description', localized_fields.fields.text_field.LocalizedTextField(blank=True, null=True, required=[], verbose_name='Описание')),
                ('video_link', localized_fields.fields.text_field.LocalizedTextField(blank=True, null=True, required=[], verbose_name='Ссылка на видео')),
                ('image', localized_fields.fields.file_field.LocalizedFileField(blank=True, null=True, required=[], upload_to='images/', verbose_name='Картинка')),
                ('chapter', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='content.chapter', verbose_name='Раздел')),
            ],
            options={
                'verbose_name': 'Тема',
                'verbose_name_plural': 'Темы',
            },
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.PositiveIntegerField(db_index=True, default=0, verbose_name='Приоритет')),
                ('name', localized_fields.fields.char_field.LocalizedCharField(null=True, required=['ru', 'kk', 'en'], verbose_name='Название')),
                ('direction', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='content.direction', verbose_name='Направление')),
            ],
            options={
                'verbose_name': 'Предмет',
                'verbose_name_plural': 'Предметы',
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.PositiveIntegerField(db_index=True, default=0, verbose_name='Приоритет')),
                ('name', localized_fields.fields.char_field.LocalizedCharField(null=True, required=['ru', 'kk', 'en'], verbose_name='Название')),
                ('grade', models.CharField(choices=[('1', 'Grade 1'), ('2', 'Grade 2'), ('3', 'Grade 3'), ('4', 'Grade 4'), ('5', 'Grade 5'), ('6', 'Grade 6'), ('7', 'Grade 7'), ('8', 'Grade 8'), ('9', 'Grade 9'), ('10', 'Grade 10'), ('11', 'Grade 11'), ('12', 'Grade 12')], default='1', max_length=3, verbose_name='Класс')),
                ('subject', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='content.subject', verbose_name='Предмет')),
            ],
            options={
                'verbose_name': 'Курс',
                'verbose_name_plural': 'Курсы',
            },
        ),
        migrations.AddField(
            model_name='chapter',
            name='course',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='content.course', verbose_name='Курс'),
        ),
    ]
