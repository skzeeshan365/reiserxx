from django.urls import path
from django.views.generic import RedirectView

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

    # Message Third
    path('3/', views.pro_1_home, name='pro_1_home'),
    path('3/exam/', views.pro_1_exam, name='pro_1_exam'),
    path('3/propose/', views.pro_1_new, name='pro_1_new'),
    path('3/accept/', views.pro_1_accept, name='pro_1_accept'),

    # Message Forth
    path('4/', views.message_4, name='message_4'),
]
