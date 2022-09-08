# Generated by Django 3.1.7 on 2022-06-22 09:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hg_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='quest',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='hg_app.player'),
        ),
        migrations.AddField(
            model_name='player',
            name='trophy_count',
            field=models.IntegerField(default=0, verbose_name='Počet trofejí'),
        ),
    ]
