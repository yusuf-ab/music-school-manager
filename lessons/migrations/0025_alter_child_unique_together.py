# Generated by Django 3.2.5 on 2022-12-03 14:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0024_alter_child_parent'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='child',
            unique_together={('first_name', 'last_name', 'parent')},
        ),
    ]
