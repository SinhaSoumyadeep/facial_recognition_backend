from django.urls import path
from . import views

urlpatterns = [
    path('match/', views.MyOwnView.as_view(), name='blog-home'),
    path('upload/', views.MyOtherView.as_view(), name='blog-dh'),
]
