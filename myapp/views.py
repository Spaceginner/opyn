from datetime import datetime
import random
import string

from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.html import escape

from .models import Paste
from .modules.markdown import compile_md


def index(request):
    return render(request, "myapp/index.html")


def view(request, paste_url: str):
    paste = get_object_or_404(Paste, url_name=paste_url)
    return render(request, "myapp/view.html", {
        'compiled': paste.compiled,
        'current_url': paste_url
    })


def raw(request, paste_url: str):
    paste = get_object_or_404(Paste, url_name=paste_url)
    return render(request, "myapp/raw.html", {
        'raw_markdown': paste.content,
        'current_url': paste_url
    })


def create(request):
    if not request.POST:
        return render(request, "myapp/create.html")
    else:
        content = request.POST['content'].strip()
        paste_url = request.POST['paste_url']
        if not paste_url:
            paste_url = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

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
            return render(request, "myapp/create.html", {
                'content': content,
                'edit_code': request.POST['edit_code'],
                'paste_url': request.POST['paste_url'],
                'error_messages': error_messages
            })

        compiled = compile_md(content)

        creation_date = datetime.today()
        paste = Paste(
            content=content,
            url_name=paste_url,
            edit_code=request.POST['edit_code'],
            compiled=compiled,
            creation_date=creation_date,
            edited_date=creation_date
        )

        try:
            paste.save()
        except IntegrityError:
            return render(request, "myapp/create.html", {
                'content': request.POST['content'],
                'edit_code': request.POST['edit_code'],
                'paste_url': request.POST['paste_url'],
                'error_messages': ['such url is already taken']
            })

        return HttpResponseRedirect(reverse("myapp:view", args=(paste_url,)))


def edit(request, paste_url: str):
    paste = get_object_or_404(Paste, url_name=paste_url)
    if not request.POST:
        return render(request, "myapp/edit.html", {
            'new_content': paste.content,
            'current_url': paste_url
        })
    else:
        new_content = request.POST['new_content'].strip()
        new_paste_url = request.POST['new_paste_url']

        error_messages = []
        if request.POST['edit_code'] != paste.edit_code:
            error_messages.append(f"invalid edit code")
        if len(new_content) > 262144:
            error_messages.append(f"new contents are too long ({len(new_content)} > 262144)")
        elif len(new_content) < 1:
            error_messages.append(f"new contents are too short ({len(new_content)} < 1)")
        if len(new_paste_url) > 256:
            error_messages.append(f"new paste url is too long ({len(new_paste_url)} > 256)")
        if len(request.POST['new_edit_code']) > 256:
            error_messages.append(f"new edit code is too long ({len(request.POST['new_edit_code'])} > 256)")
        if error_messages:
            return render(request, "myapp/edit.html", {
                'new_content': new_content,
                'new_edit_code': request.POST['new_edit_code'],
                'new_paste_url': request.POST['new_paste_url'],
                'error_messages': error_messages,
                'current_url': paste_url
            })

        paste.content = new_content
        if new_paste_url:
            paste.url_name = new_paste_url
        if request.POST['new_edit_code']:
            paste.edit_code = request.POST['new_edit_code']
        paste.edited_date = datetime.today()

        paste.compiled = compile_md(escape(new_content))

        try:
            paste.save()
        except IntegrityError:
            return render(request, "myapp/edit.html", {
                'new_content': request.POST['new_content'],
                'new_edit_code': request.POST['new_edit_code'],
                'new_paste_url': request.POST['new_paste_url'],
                'error_messages': ['such new url is already taken'],
                'current_url': paste_url
            })

        return HttpResponseRedirect(reverse("myapp:view", args=(new_paste_url if new_paste_url else paste_url,)))


# error handlers

def page_not_found(request, exception=None):
    return render(request, "myapp/error.html", {'error_code': 404})


def server_error(request, exception=None):
    return render(request, "myapp/error.html", {'error_code': 500})


def bad_request(request, exception=None):
    return render(request, "myapp/error.html", {'error_code': 400})
