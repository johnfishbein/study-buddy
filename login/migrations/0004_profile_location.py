# Generated by Django 3.0.2 on 2020-04-10 21:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0003_auto_20200406_0432'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='location',
            field=models.CharField(default='Not tutoring', max_length=200),
        ),
    ]