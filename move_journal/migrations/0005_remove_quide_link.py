# Generated by Django 2.1.15 on 2022-08-17 13:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('move_journal', '0004_auto_20220816_1343'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quide',
            name='link',
        ),
    ]
