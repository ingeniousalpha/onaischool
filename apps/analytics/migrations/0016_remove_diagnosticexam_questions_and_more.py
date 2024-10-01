# Generated by Django 4.0 on 2024-10-01 20:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0015_diagnosticexamquestion_diagnosticexamansweroption_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='diagnosticexam',
            name='questions',
        ),
        migrations.AddField(
            model_name='diagnosticexamquestion',
            name='diagnostic_exam',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='diagnostic_exam_questions', to='analytics.diagnosticexam', verbose_name='Диагностический тест'),
        ),
    ]
