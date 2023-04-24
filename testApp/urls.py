from django.urls import path
from . import views

urlpatterns = [
    path('', views.predict, name='apsa'),
    path('predict/', views.predict, name='predict'),
]
