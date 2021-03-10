from django.shortcuts import render
from msc_download import models

# Create your views here.

def index(request):

    msc=models.Musiclist.objects.all()
    data={
        'msc':msc
    }

    return render(request,'music.html',data)