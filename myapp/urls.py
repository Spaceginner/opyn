from django.urls import path

from . import views

app_name = "myapp"
urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create, name="create"),
    path("<slug:paste_url>", views.view, name="view"),
    path("<slug:paste_url>/edit", views.edit, name="edit"),
    path("<slug:paste_url>/raw", views.raw, name="raw"),
    path("status/404/", views.page_not_found, name="page_not_found"),
    path("status/500/", views.server_error, name="server_error"),
    path("status/400/", views.page_not_found, name="bad_request")
]
