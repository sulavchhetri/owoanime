# Generated by Django 3.2.3 on 2021-06-09 02:06

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ViewsCounter',
            fields=[
                ('page', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('views', models.IntegerField(default=0)),
            ],
        ),
    ]
