from django.urls import path

from . import views

app_name = "myapp"
urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create, name="create"),
    path("<slug:paste_url>", views.view, name="view"),
    path("<slug:paste_url>/edit", views.edit, name="edit")
]
