
from django.contrib import admin
from django.urls import path, include

from mirror import views

app_name = 'mirror'


urlpatterns = [
    path('set_clip/', views.set_clip),
    path('get_clip/', views.get_clip),
]
