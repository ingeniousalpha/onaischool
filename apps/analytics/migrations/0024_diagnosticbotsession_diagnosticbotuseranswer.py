# Generated by Django 4.0 on 2025-01-06 20:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0023_entranceexamperday_show_result_on_dashboard'),
    ]

    operations = [
        migrations.CreateModel(
            name='DiagnosticBotSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.BigIntegerField(verbose_name='ID  пользователя')),
                ('message_id', models.IntegerField(verbose_name='ID  сообщения')),
                ('language', models.CharField(default='ru', max_length=3, verbose_name='Язык')),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True, verbose_name='Номер телефона')),
            ],
            options={
                'verbose_name': 'Диагностика пользователя',
                'verbose_name_plural': 'Диагностика пользователей',
            },
        ),
        migrations.CreateModel(
            name='DiagnosticBotUserAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analytics.diagnosticexamansweroption', verbose_name='Ответ пользователя')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analytics.diagnosticexamquestion', verbose_name='Вопрос')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analytics.diagnosticbotsession', verbose_name='Сессия')),
            ],
            options={
                'verbose_name': 'Ответ пользователя',
                'verbose_name_plural': 'Ответы пользователя',
            },
        ),
    ]
