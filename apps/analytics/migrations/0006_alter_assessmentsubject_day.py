# Generated by Django 4.0 on 2024-08-16 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0005_assessmentsubject_day'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assessmentsubject',
            name='day',
            field=models.CharField(choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4')], default='1', max_length=100, verbose_name='Какой день'),
        ),
    ]
