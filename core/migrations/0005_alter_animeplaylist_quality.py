# Generated by Django 4.0.4 on 2022-05-13 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_animeplaylist_date_aired_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='animeplaylist',
            name='quality',
            field=models.TextField(blank=True, null=True),
        ),
    ]