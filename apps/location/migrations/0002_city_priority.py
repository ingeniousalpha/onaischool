# Generated by Django 4.0 on 2024-08-01 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='priority',
            field=models.PositiveIntegerField(db_index=True, default=0, verbose_name='Приоритет'),
        ),
    ]
