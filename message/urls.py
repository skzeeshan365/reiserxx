from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='message_home'),
    path('no/', views.no, name='message_no'),
    path('no2/', views.no_2, name='message_no2'),
    path('yes/', views.yes, name='message_yes'),
    path('yes2/', views.yes_1, name='message_yes2'),
]
