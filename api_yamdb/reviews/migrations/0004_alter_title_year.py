# Generated by Django 3.2 on 2025-03-13 12:56

from django.db import migrations, models
import reviews.validators


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0003_alter_title_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='title',
            name='year',
            field=models.SmallIntegerField(db_index=True, validators=[reviews.validators.year_not_in_future], verbose_name='Год издания'),
        ),
    ]
