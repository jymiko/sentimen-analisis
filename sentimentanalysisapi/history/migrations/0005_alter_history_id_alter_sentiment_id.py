# Generated by Django 4.1.3 on 2022-11-13 08:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("history", "0004_auto_20210302_1952"),
    ]

    operations = [
        migrations.AlterField(
            model_name="history",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="sentiment",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]
