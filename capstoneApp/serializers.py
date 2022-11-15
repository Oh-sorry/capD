from rest_framework import serializers
from .models import userinfo, item_list, refrigerator_item, recipe_list, recipe_item_list


class UserinfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = userinfo
        fields = ['username', 'userid', 'password']


class Item_ListSerializer(serializers.ModelSerializer):
    class Meta:
        model = item_list
        fields = ['item_name']


class RefrigeratorItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = refrigerator_item
        fields = ['userid', 'item_name', 'insert_date', 'item_counts']


class RecipeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = recipe_list
        fields = ['recipe_name']


class RecipeItemList(serializers.ModelSerializer):
    class Meta:
        model = recipe_item_list
        fields = ['recipe_name', 'item_name', 'item_importance']

# class RunningDataSerializer(serializers.ModelSerializer):
#     class Meta:

