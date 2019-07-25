
from django.contrib import admin
from django.urls import path, include

from mirror import views

app_name = 'mirror'


urlpatterns = [
    path('clipboards/<token>/', views.clipboard),
]
