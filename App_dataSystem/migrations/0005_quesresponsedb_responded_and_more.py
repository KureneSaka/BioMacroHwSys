# Generated by Django 4.2.5 on 2023-10-12 00:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App_dataSystem', '0004_rename_evaluate_quesevaluatedb_evaluation'),
    ]

    operations = [
        migrations.AddField(
            model_name='quesresponsedb',
            name='responded',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='quesresponsedb',
            name='response',
            field=models.TextField(blank=True),
        ),
    ]
