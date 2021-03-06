# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-02-15 06:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('email', models.EmailField(max_length=250)),
                ('account', models.BooleanField()),
                ('password', models.CharField(max_length=260)),
                ('org_Events', models.CharField(max_length=1000)),
                ('part_Events', models.CharField(max_length=1000)),
            ],
        ),
    ]
