from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='ai_home'),
    path('multimodel/', views.multimodel, name='ai_multimodel'),
    ]
