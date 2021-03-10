from django.urls import path, include
from msc_download import views

urlpatterns = [
    path('music/',views.index)
]