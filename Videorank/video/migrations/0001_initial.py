# Generated by Django 2.2 on 2020-07-29 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Videolist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rank', models.IntegerField()),
                ('title', models.CharField(max_length=100)),
                ('url', models.CharField(max_length=100)),
                ('grade', models.IntegerField()),
            ],
        ),
    ]
