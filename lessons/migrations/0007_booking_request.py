# Generated by Django 3.2.5 on 2022-11-14 18:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0006_alter_user_role'),
    ]

    operations = [
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('availability', models.CharField(max_length=1000)),
                ('lessons', models.IntegerField()),
                ('days_between_lessons', models.IntegerField()),
                ('duration', models.IntegerField()),
                ('info', models.CharField(max_length=1000)),
                ('fulfilled', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lessons', models.IntegerField()),
                ('days_between_lessons', models.IntegerField()),
                ('duration', models.IntegerField()),
                ('time', models.DateTimeField()),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]