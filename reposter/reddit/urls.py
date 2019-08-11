from django.urls import path

from . import views

app_name = 'reddit'
urlpatterns = [
    path('', views.index, name='index'),
]
