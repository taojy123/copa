
from django.contrib import admin
from django.urls import path, include

from mirror import views

app_name = 'mirror'


urlpatterns = [
    path('status/', views.status),
    path('push/', views.push),
    path('pull/', views.pull),
]
