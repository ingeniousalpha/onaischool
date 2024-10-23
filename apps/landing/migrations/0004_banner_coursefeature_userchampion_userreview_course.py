# Generated by Django 4.0 on 2024-10-18 17:38

from django.db import migrations, models
import localized_fields.fields.char_field
import localized_fields.fields.text_field


class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0003_delete_userquestion_alter_teacher_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Banner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.PositiveIntegerField(db_index=True, default=0, verbose_name='Приоритет')),
                ('description', localized_fields.fields.text_field.LocalizedTextField(blank=True, null=True, required=[], verbose_name='Описание')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Время создания')),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True, verbose_name='Время последнего изменения')),
                ('title', localized_fields.fields.char_field.LocalizedCharField(blank=True, null=True, required=[], verbose_name='Заголовок')),
                ('image', models.ImageField(upload_to='', verbose_name='Backgroud image')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CourseFeature',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.PositiveIntegerField(db_index=True, default=0, verbose_name='Приоритет')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Время создания')),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True, verbose_name='Время последнего изменения')),
                ('title', localized_fields.fields.char_field.LocalizedCharField(blank=True, null=True, required=[], verbose_name='Заголовок')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserChampion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.PositiveIntegerField(db_index=True, default=0, verbose_name='Приоритет')),
                ('description', localized_fields.fields.text_field.LocalizedTextField(blank=True, null=True, required=[], verbose_name='Описание')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Время создания')),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True, verbose_name='Время последнего изменения')),
                ('image', models.ImageField(upload_to='', verbose_name='Картинка')),
                ('full_name', models.CharField(max_length=200, verbose_name='Имя/Фамилия')),
            ],
            options={
                'verbose_name': 'Чемпион',
                'verbose_name_plural': 'Чемпионы',
            },
        ),
        migrations.CreateModel(
            name='UserReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.PositiveIntegerField(db_index=True, default=0, verbose_name='Приоритет')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Время создания')),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True, verbose_name='Время последнего изменения')),
            ],
            options={
                'verbose_name': 'Отзыв',
                'verbose_name_plural': 'Отзывы',
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.PositiveIntegerField(db_index=True, default=0, verbose_name='Приоритет')),
                ('description', localized_fields.fields.text_field.LocalizedTextField(blank=True, null=True, required=[], verbose_name='Описание')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Время создания')),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True, verbose_name='Время последнего изменения')),
                ('title', localized_fields.fields.char_field.LocalizedCharField(blank=True, null=True, required=[], verbose_name='Заголовок')),
                ('features', models.ManyToManyField(blank=True, null=True, to='landing.CourseFeature')),
            ],
            options={
                'verbose_name': 'Курс',
                'verbose_name_plural': 'Курсы',
            },
        ),
    ]