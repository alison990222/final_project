# Generated by Django 2.2.5 on 2019-09-07 05:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_pic'),
    ]

    operations = [
        migrations.AddField(
            model_name='pic',
            name='url',
            field=models.URLField(blank=True),
        ),
        migrations.AlterField(
            model_name='pic',
            name='picture',
            field=models.ImageField(blank=True, upload_to='pictures'),
        ),
    ]