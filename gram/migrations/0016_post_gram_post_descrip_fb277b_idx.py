# Generated by Django 3.2.5 on 2021-07-29 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gram', '0015_alter_post_user'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='post',
            index=models.Index(fields=['description'], name='gram_post_descrip_fb277b_idx'),
        ),
    ]