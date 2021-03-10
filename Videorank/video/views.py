from django.shortcuts import render

# Create your views here.
from video import models


def show(request):

    vi=models.Videolist.objects.all()

    data={
        'vi':vi
    }

    return render(request,'rank.html',data)