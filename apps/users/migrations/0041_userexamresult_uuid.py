# Generated by Django 4.0 on 2024-11-15 21:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0040_userexamquestion_user_answer'),
    ]

    operations = [
        migrations.AddField(
            model_name='userexamresult',
            name='uuid',
            field=models.UUIDField(editable=False, null=True, unique=True),
        ),
    ]
