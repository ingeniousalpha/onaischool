# Generated by Django 4.0 on 2024-09-27 15:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0011_subject_enable_sor_sosh'),
        ('users', '0029_userassessment_userassessmentresult'),
    ]

    operations = [
        migrations.AddField(
            model_name='userassessment',
            name='course',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_assessments', to='content.course'),
        ),
        migrations.AddField(
            model_name='userassessment',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_assessments', to='users.user', verbose_name='Пользователь'),
        ),
    ]
