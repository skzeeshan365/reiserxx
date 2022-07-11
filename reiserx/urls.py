from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('policy/', views.policy, name="policy"),
    path('terms of use/', views.terms, name="terms of use"),
    path('contact', views.contact, name="contact"),
]
