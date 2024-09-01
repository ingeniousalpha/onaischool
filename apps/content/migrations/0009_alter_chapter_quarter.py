# Generated by Django 4.0 on 2024-08-06 18:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0008_alter_chapter_options_alter_course_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chapter',
            name='quarter',
            field=models.CharField(choices=[('1', '1 четверть'), ('2', '2 четверть'), ('3', '3 четверть'), ('4', '4 четверть')], default='1', max_length=10, verbose_name='Четверть'),
        ),
    ]