# Generated by Django 4.2.1 on 2023-05-22 01:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0006_remove_user_image'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='user_image',
            new_name='image',
        ),
    ]
