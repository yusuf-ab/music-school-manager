# Generated by Django 3.2.5 on 2022-11-14 23:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0007_booking_request'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='client',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, related_name='client', to='lessons.user'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='request',
            name='client',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='lessons.user'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='booking',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='teacher', to=settings.AUTH_USER_MODEL),
        ),
    ]
