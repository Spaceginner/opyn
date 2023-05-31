import random
import string

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse


def index(request):
    return render(request, "myapp/index.html")


def view(request, paste_url: str):
    return render(request, "myapp/view.html")


def create(request):
    paste_url = request.POST['paste_url']

    if not paste_url:
        paste_url = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    return HttpResponseRedirect(reverse("myapp:view", args=(paste_url,)))


def edit(request, paste_url: str):
    return render(request, "myapp/edit.html")
