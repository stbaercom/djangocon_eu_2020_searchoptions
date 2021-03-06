# Generated by Django 3.0.3 on 2020-07-16 07:58

import django.contrib.postgres.indexes
import django.contrib.postgres.search
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_search_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FTSReview',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('productId', models.CharField(max_length=200)),
                ('userId', models.CharField(max_length=200)),
                ('name', models.CharField(max_length=200)),
                ('review_help_total', models.PositiveIntegerField()),
                ('review_help_help', models.PositiveIntegerField()),
                ('review_score', models.FloatField()),
                ('review_time', models.DateTimeField()),
                ('review_summary', models.TextField()),
                ('review_text', models.TextField()),
                ('review_index', django.contrib.postgres.search.SearchVectorField(null=True)),
            ],
        ),
        migrations.AddIndex(
            model_name='ftsreview',
            index=django.contrib.postgres.indexes.GinIndex(fields=['review_index'], name='django_sear_review__2a6178_gin'),
        ),
    ]
