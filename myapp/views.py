from django.shortcuts import render


def index(request):
    return render(request, "myapp/index.html")


def view(request, paste_url: str):
    return render(request, "myapp/view.html")


def create(request):
    return render(request, "myapp/create.html")


def edit(request, paste_url: str):
    return render(request, "myapp/edit.html")
