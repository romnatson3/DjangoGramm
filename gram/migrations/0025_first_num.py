# Generated by Django 3.2.5 on 2021-09-27 10:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gram', '0024_main2'),
    ]

    operations = [
        migrations.AddField(
            model_name='first',
            name='num',
            field=models.TextField(blank=True, null=True),
        ),
    ]