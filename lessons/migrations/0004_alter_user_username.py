# Generated by Django 4.1.2 on 2022-11-08 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0003_remove_user_type_user_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=30, unique=True),
        ),
    ]
