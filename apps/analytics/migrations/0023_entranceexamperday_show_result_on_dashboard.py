# Generated by Django 4.0 on 2024-11-11 21:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0022_alter_examquestion_explanation_answer_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='entranceexamperday',
            name='show_result_on_dashboard',
            field=models.BooleanField(default=False, verbose_name='Показать в дачбоарде'),
        ),
    ]
