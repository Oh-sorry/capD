from django.db import models
from datetime import datetime

class userinfo(models.Model):
    username = models.CharField(max_length=30, null=False)
    userid = models.CharField(max_length=30, null=False, primary_key=True)
    password = models.CharField(max_length=30, null=False)


    class Meta:
        #정렬
        #ordering = ('userid',)
        db_table = 'userinfo'

    def __str__(self):
        return self.userid


#재료_list , 직접 수기로 만들어줘야함
class item_list(models.Model):
    item_name = models.CharField(max_length=100, null=False,primary_key=True)


    class Meta:
        db_table = 'item_list'


#냉장고DB
class refrigerator_item(models.Model):
    userid = models.ForeignKey('userinfo', on_delete=models.CASCADE, db_column='userid')
    item_name = models.ForeignKey('item_list', on_delete=models.CASCADE, db_column='item_id')
    insert_date = models.DateField(auto_now_add=True, blank=True)
    item_counts = models.IntegerField(db_column='item_counts', null=False)

    class Meta:
        db_table = 'refrigerator_item'


#레시피_LIst , 직접수기로 만들어줘야함
class recipe_list(models.Model):
    recipe_name = models.CharField(primary_key=True, max_length=100, null=False)

    class Meta:
        db_table = 'recipe_list'


#레시피재료_list , 직접 수기로 만들어줘야함
class recipe_item_list(models.Model):
    recipe_name = models.ForeignKey('recipe_list', on_delete=models.CASCADE, db_column='recipe_name')
    item_name = models.ForeignKey('item_list', on_delete=models.CASCADE, db_column='item_name')
    item_importance = models.CharField(max_length=20, null=False)


    class Meta:
        db_table = 'recipe_item_list'


#레시피과정&순서 , 직접 수기로 만들어줘야함
class recipe_process(models.Model):
    recipe_name = models.ForeignKey('recipe_list', on_delete=models.CASCADE, db_column='recipe_name')
    order = models.IntegerField(null=False)
    process = models.CharField(max_length=2000, null=False)

    class Meta:
        db_table = 'recipe_process'