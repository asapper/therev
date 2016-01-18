# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-18 00:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Finishing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('finishing_name', models.CharField(max_length=100)),
                ('finishing_price', models.DecimalField(decimal_places=2, max_digits=6)),
            ],
        ),
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('material_name', models.CharField(max_length=100)),
                ('material_price', models.DecimalField(decimal_places=2, max_digits=6)),
            ],
        ),
        migrations.CreateModel(
            name='Paper',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paper_name', models.CharField(max_length=100)),
                ('paper_width', models.DecimalField(decimal_places=2, max_digits=4)),
                ('paper_length', models.DecimalField(decimal_places=2, max_digits=4)),
                ('paper_price', models.DecimalField(decimal_places=2, max_digits=5)),
            ],
        ),
    ]
