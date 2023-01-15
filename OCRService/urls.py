from django.urls import path
from . import views

urlpatterns = [
    path('api/', views.scan_document, name='run'),
    path('web/', views.index, name='runweb'),
    path('web/run', views.runcode, name='runweb'),
]
