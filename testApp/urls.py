from django.urls import path
from . import views

urlpatterns = [
    path('', views.wish, name='wish'),
]
