from django.urls import path
from . import views

urlpatterns = [
    path('', views.MyOwnView.as_view(), name='blog-home'),
]
