# Generated by Django 4.1.1 on 2022-10-27 07:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('capstoneApp', '0002_alter_refrigerator_item_insert_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='refrigerator_item',
            name='item_name',
            field=models.ForeignKey(db_column='item_name', on_delete=django.db.models.deletion.CASCADE, to='capstoneApp.item_list'),
        ),
    ]
