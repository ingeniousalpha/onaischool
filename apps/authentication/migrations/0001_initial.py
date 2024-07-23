# Generated by Django 4.1.7 on 2024-07-23 14:36

from django.db import migrations, models
import django.utils.timezone
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='VerifiedOTP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name='Время создания')),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True, verbose_name='Время последнего изменения')),
                ('mobile_phone', models.CharField(max_length=12)),
                ('otp_code', models.CharField(max_length=6)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OTP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name='Время создания')),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True, verbose_name='Время последнего изменения')),
                ('code', models.CharField(db_index=True, editable=False, max_length=12, verbose_name='OTP')),
                ('verified', models.BooleanField(default=False, editable=False, verbose_name='Подтверждён')),
                ('mobile_phone', phonenumber_field.modelfields.PhoneNumberField(editable=False, max_length=128, region=None, verbose_name='Мобильный телефон')),
            ],
            options={
                'verbose_name': 'Одноразовый пароль',
                'verbose_name_plural': 'Одноразовые пароли',
                'unique_together': {('code', 'mobile_phone')},
            },
        ),
    ]
