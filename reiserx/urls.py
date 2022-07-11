from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('policy/', views.policy, name="policy"),
    path('terms/', views.policy, name="terms of use"),
]
