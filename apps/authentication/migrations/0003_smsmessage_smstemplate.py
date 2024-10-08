# Generated by Django 4.0 on 2024-09-18 17:44

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_alter_otp_created_at_alter_verifiedotp_created_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='SMSMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Время создания')),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True, verbose_name='Время последнего изменения')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='Идентификатор')),
                ('recipients', models.CharField(editable=False, max_length=255, verbose_name='Получатели')),
                ('content', models.TextField(editable=False, verbose_name='Содержимое')),
                ('error_code', models.IntegerField(editable=False, null=True, verbose_name='Код ошибки')),
                ('error_description', models.CharField(editable=False, max_length=255, null=True, verbose_name='Описание ошибки')),
            ],
            options={
                'verbose_name': 'SMS сообщение',
                'verbose_name_plural': 'SMS сообщения',
            },
        ),
        migrations.CreateModel(
            name='SMSTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('OTP', 'Отправка одноразового пароля')], max_length=32, unique=True, verbose_name='Наименование')),
                ('content', models.TextField(verbose_name='Содержимое')),
            ],
            options={
                'verbose_name': 'Шаблон СМС',
                'verbose_name_plural': 'Шаблоны СМС',
            },
        ),
    ]
