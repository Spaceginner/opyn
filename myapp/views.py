from datetime import datetime
import random
import string

from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from .models import Paste


def index(request):
    return render(request, "myapp/index.html")


# TODO create a markdown engine
# TODO redirect user to `create` page if 404
def view(request, paste_url: str):
    paste = get_object_or_404(Paste, url_name=paste_url)
    return render(request, "myapp/view.html", {
        'content': paste.content
    })


# TODO hash the edit code
def create(request):
    content = request.POST['content'].trim()
    paste_url = request.POST['paste_url']
    if not paste_url:
        paste_url = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    # TODO test for availability of `paste_url` here, instead of relying on `IntegrityError`
    error_messages = []
    if len(content) > 262144:
        error_messages.append(f"contents is too long ({len(content)} > 262144)")
    elif len(content) < 1:
        error_messages.append(f"contents are too short ({len(content)} < 1)")
    if len(paste_url) > 256:
        error_messages.append(f"paste url is too long ({len(paste_url)} > 256)")
    if len(request.POST['edit_code']) > 256:
        error_messages.append(f"edit code is too long ({len(request.POST['edit_code'])} > 256)")
    elif len(request.POST['edit_code']) < 1:
        error_messages.append(f"edit code is too short ({len(request.POST['edit_code'])} < 1)")
    if error_messages:
        return render(request, "myapp/index.html", {
            'content': content,
            'edit_code': request.POST['edit_code'],
            'paste_url': request.POST['paste_url'],
            'error_messages': error_messages
        })

    creation_date = datetime.today()
    paste = Paste(
        content=content,
        url_name=paste_url,
        edit_code=request.POST['edit_code'],
        creation_date=creation_date,
        edited_date=creation_date
    )

    try:
        paste.save()
    except IntegrityError:
        return render(request, "myapp/index.html", {
            'content': request.POST['content'],
            'edit_code': request.POST['edit_code'],
            'paste_url': request.POST['paste_url'],
            'error_messages': ['such url is already taken']
        })

    return HttpResponseRedirect(reverse("myapp:view", args=(paste_url,)))


def edit(request, paste_url: str):
    return render(request, "myapp/edit.html")
