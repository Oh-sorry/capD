from django.contrib import admin
from django.urls import path, include
from capstoneApp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('index/', views.index),
    path('login/', views.login),
    path('signup/', views.signup),
    path('textrunning/', views.textrunning),
    path('getMyRefrigerator/', views.getMyRefrigerator),
    path('getMyRecipe/', views.getMyRecipe),
    path('saveItem/', views.saveItem),
    path('removeItem/', views.removeItem),
    path('updateItem/', views.updateItem),
    path('getRecipeProcess/', views.getRecipeProcess),
    path('useRecipe/', views.useRecipe),
    path('userAddItem/', views.userAddItem),

]
