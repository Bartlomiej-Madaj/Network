# Generated by Django 4.2.1 on 2023-05-21 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0004_alter_user_user_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_image',
            field=models.ImageField(default='images/default-avatar-profile.jpg', null=True, upload_to='images'),
        ),
    ]
