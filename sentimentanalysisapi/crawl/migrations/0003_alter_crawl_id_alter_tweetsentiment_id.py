# Generated by Django 4.1.3 on 2022-11-13 08:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("crawl", "0002_tweetsentiment"),
    ]

    operations = [
        migrations.AlterField(
            model_name="crawl",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="tweetsentiment",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]
