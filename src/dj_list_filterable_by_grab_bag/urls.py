from django.urls import path

from dj_list_filterable_by_grab_bag import views

urlpatterns = [
    path('', views.home, name='home'),
    path('items/', views.item_list, name='item-list'),
]
