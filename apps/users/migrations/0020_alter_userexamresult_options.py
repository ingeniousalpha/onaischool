# Generated by Django 4.0 on 2024-09-04 18:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0019_alter_mytopic_options_userexamresult_exam_per_day'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userexamresult',
            options={'ordering': ['-created_at']},
        ),
    ]