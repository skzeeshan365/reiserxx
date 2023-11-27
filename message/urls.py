from django.urls import path

from . import views

urlpatterns = [
    # Home
    path('', views.home, name='message_home'),

    # Message First
    path('1/', views.first_home, name='message_first_home'),
    path('1/no/', views.first_no, name='message_first_no'),
    path('1/no2/', views.first_no_2, name='message_first_no2'),
    path('1/yes/', views.first_yes, name='message_first_yes'),
    path('1/yes2/', views.first_yes_1, name='message_first_yes2'),

    # Message Second
    path('2/', views.second_home, name='message_two_home'),
    path('2/mail/', views.second_mail, name='message_two_mail'),
]
