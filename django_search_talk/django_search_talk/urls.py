from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('reviews/', include('django_search_app.urls', namespace="search")),
    path('admin/', admin.site.urls),
]