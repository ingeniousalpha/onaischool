# Generated by Django 4.0 on 2024-09-26 20:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0010_direction_enable_all'),
    ]

    operations = [
        migrations.AddField(
            model_name='subject',
            name='enable_sor_sosh',
            field=models.BooleanField(default=False, verbose_name='Сор/Соч разрешен'),
        ),
    ]
