# Generated by Django 4.0.4 on 2022-05-02 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hg_app', '0015_remove_point_codes_point_picked_up_alter_package_lat_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='point',
            name='max_number_of_visits',
            field=models.IntegerField(default=0),
        ),
        migrations.RemoveField(
            model_name='point',
            name='picked_up',
        ),
        migrations.AddField(
            model_name='point',
            name='picked_up',
            field=models.ManyToManyField(blank=True, to='hg_app.player'),
        ),
    ]
