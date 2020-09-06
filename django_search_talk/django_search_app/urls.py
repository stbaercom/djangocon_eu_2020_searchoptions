from django.urls import path

from . import views

app_name = 'search'

urlpatterns = [
    path('', views.review_list, name='review_list'),
    path('search', views.search_list, name='search_list'),
    path('<str:pid>/<str:uid>', views.review_detail, name='review_detail'),
]
