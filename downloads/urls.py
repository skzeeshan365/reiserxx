from django.urls import path
from . import views

urlpatterns = [
    path('', views.download, name='download'),
    path('downloadfiles', views.downloadfiles, name='downloadfiles'),
]
