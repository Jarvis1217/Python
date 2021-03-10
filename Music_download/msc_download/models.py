from django.db import models

# Create your models here.

class Musiclist(models.Model):

    playlist=models.CharField(max_length=100)
    Musicname=models.CharField(max_length=50)
    url=models.CharField(max_length=100)
