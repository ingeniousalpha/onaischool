# Generated by Django 4.0 on 2024-08-16 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0004_alter_question_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessmentsubject',
            name='day',
            field=models.CharField(choices=[('first', '1'), ('two', '2'), ('three', '3'), ('four', '4')], default='first', max_length=100, verbose_name='Какой день'),
        ),
    ]
