from django.urls import path, include

from video import views

urlpatterns = [

    path('index/',views.show)
]