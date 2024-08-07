# Generated by Django 4.1.7 on 2024-07-23 14:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import phonenumber_field.modelfields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('uuid', models.UUIDField(default=uuid.uuid4, unique=True, verbose_name='UUID пользователя')),
                ('email', models.EmailField(max_length=40, unique=True, verbose_name='Почта')),
                ('mobile_phone', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None, verbose_name='Моб. телефон')),
                ('secret_key', models.UUIDField(default=uuid.uuid4, unique=True, verbose_name='Секретный ключ')),
                ('language', models.CharField(choices=[('kk', 'Казахский'), ('ru', 'Русский'), ('en', 'Английский')], default='kk', max_length=20, verbose_name='Язык')),
                ('grade', models.CharField(choices=[('1', 'Grade 1'), ('2', 'Grade 2'), ('3', 'Grade 3'), ('4', 'Grade 4'), ('5', 'Grade 5'), ('6', 'Grade 6'), ('7', 'Grade 7'), ('8', 'Grade 8'), ('9', 'Grade 9'), ('10', 'Grade 10'), ('11', 'Grade 11'), ('12', 'Grade 12')], default='1', max_length=3, verbose_name='Класс')),
                ('role', models.CharField(choices=[('parent', 'Parent'), ('student', 'Student'), ('mentor', 'Mentor'), ('admin', 'Admin')], default='student', max_length=50)),
                ('is_active', models.BooleanField(default=True, verbose_name='Активный')),
                ('is_staff', models.BooleanField(default=False, verbose_name='Сотрудник')),
                ('is_email_confirmed', models.BooleanField(default=False, verbose_name='Почта подтверждена')),
                ('is_mobile_phone_verified', models.BooleanField(default=False)),
                ('avatar_image', models.ImageField(blank=True, null=True, upload_to='')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Создан')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлен')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to=settings.AUTH_USER_MODEL, verbose_name='Родитель')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Учетная запись',
                'verbose_name_plural': 'Учетная запись',
            },
        ),
    ]
