# Generated by Django 4.0 on 2024-08-05 19:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0007_school_city'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='chapter',
            options={'ordering': ['quarter', 'priority'], 'verbose_name': 'Раздел', 'verbose_name_plural': 'Разделы'},
        ),
        migrations.AlterModelOptions(
            name='course',
            options={'ordering': ['grade', 'priority'], 'verbose_name': 'Курс', 'verbose_name_plural': 'Курсы'},
        ),
    ]
