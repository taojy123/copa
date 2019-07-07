
from django.contrib import admin
from django.urls import path, include

from mirror import views

app_name = 'mirror'


urlpatterns = [
    path('push/', views.push),
    path('fetch/', views.fetch),
    path('savepoints/', views.savepoints),
    path('loadpoint/', views.loadpoint),
]
