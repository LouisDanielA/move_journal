# Generated by Django 2.1.15 on 2022-09-08 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('move_journal', '0008_auto_20220908_1134'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quide',
            name='formula',
            field=models.TextField(blank=True, default='', null=True, verbose_name='Формула'),
        ),
    ]
