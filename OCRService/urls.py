from django.urls import path
from . import views

urlpatterns = [
    path('', views.process, name='run'),
    path('web/', views.index, name='runweb'),
    path('web/run', views.runcode, name='runweb'),
]
