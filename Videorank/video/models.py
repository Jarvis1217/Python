from django.db import models

# Create your models here.
class Videolist(models.Model):
    rank=models.IntegerField()
    title=models.CharField(max_length=100)
    url=models.CharField(max_length=100)
    grade=models.IntegerField()