# Generated by Django 3.1.7 on 2022-06-28 11:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hg_app', '0005_auto_20220628_1250'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='kill',
            options={'verbose_name': 'Kill', 'verbose_name_plural': 'Killy'},
        ),
        migrations.AlterModelOptions(
            name='player',
            options={'verbose_name': 'Hráč', 'verbose_name_plural': 'Hráči'},
        ),
        migrations.AlterModelOptions(
            name='specialaction',
            options={'verbose_name': 'Speciální akce', 'verbose_name_plural': 'Speciální akce'},
        ),
    ]