# Generated by Django 5.0.1 on 2024-02-07 08:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0005_post"),
    ]

    operations = [
        migrations.CreateModel(
            name="LikePosts",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("post_id", models.CharField(max_length=500)),
                ("username", models.CharField(max_length=100)),
            ],
        ),
    ]