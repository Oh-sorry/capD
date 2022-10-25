# Generated by Django 4.0.4 on 2022-10-20 12:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='item_list',
            fields=[
                ('item_name', models.CharField(max_length=100, primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'item_list',
            },
        ),
        migrations.CreateModel(
            name='recipe_list',
            fields=[
                ('recipe_name', models.CharField(max_length=100, primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'recipe_list',
            },
        ),
        migrations.CreateModel(
            name='userinfo',
            fields=[
                ('username', models.CharField(max_length=30)),
                ('userid', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('password', models.CharField(max_length=30)),
            ],
            options={
                'db_table': 'userinfo',
            },
        ),
        migrations.CreateModel(
            name='refrigerator_item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('insert_date', models.DateTimeField(auto_now_add=True)),
                ('item_counts', models.IntegerField(db_column='item_counts')),
                ('item_name', models.ForeignKey(db_column='item_id', on_delete=django.db.models.deletion.CASCADE, to='capstoneApp.item_list')),
                ('userid', models.ForeignKey(db_column='userid', on_delete=django.db.models.deletion.CASCADE, to='capstoneApp.userinfo')),
            ],
            options={
                'db_table': 'refrigerator_item',
            },
        ),
        migrations.CreateModel(
            name='recipe_process',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField()),
                ('process', models.CharField(max_length=2000)),
                ('recipe_name', models.ForeignKey(db_column='recipe_name', on_delete=django.db.models.deletion.CASCADE, to='capstoneApp.recipe_list')),
            ],
            options={
                'db_table': 'recipe_process',
            },
        ),
        migrations.CreateModel(
            name='recipe_item_list',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_importance', models.CharField(max_length=20)),
                ('item_name', models.ForeignKey(db_column='item_name', on_delete=django.db.models.deletion.CASCADE, to='capstoneApp.item_list')),
                ('recipe_name', models.ForeignKey(db_column='recipe_name', on_delete=django.db.models.deletion.CASCADE, to='capstoneApp.recipe_list')),
            ],
            options={
                'db_table': 'recipe_item_list',
            },
        ),
    ]