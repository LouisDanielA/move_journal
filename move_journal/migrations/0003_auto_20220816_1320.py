# Generated by Django 2.1.15 on 2022-08-16 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('move_journal', '0002_auto_20220816_1127'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='formula',
            options={'managed': True, 'verbose_name': 'Формула', 'verbose_name_plural': 'Формула'},
        ),
        migrations.AlterModelOptions(
            name='quide',
            options={'managed': True, 'verbose_name': 'Справочник', 'verbose_name_plural': 'Справочник'},
        ),
        migrations.AlterModelOptions(
            name='value',
            options={'managed': True, 'verbose_name': 'Данные', 'verbose_name_plural': 'Данные'},
        ),
        migrations.AlterField(
            model_name='quide',
            name='name',
            field=models.CharField(blank=True, default='', max_length=255, null=True, verbose_name='Название'),
        ),
    ]
