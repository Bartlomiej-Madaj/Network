# Generated by Django 4.2.1 on 2023-05-21 15:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0005_alter_user_user_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='image',
        ),
    ]
