# Generated by Django 4.0 on 2024-09-26 19:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0010_direction_enable_all'),
        ('analytics', '0012_alter_entranceexamperday_exam'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entranceexam',
            name='direction',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='entrance_exams', to='content.direction', verbose_name='Направление'),
        ),
    ]
