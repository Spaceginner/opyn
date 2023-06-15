import hashlib
from datetime import datetime
import random
import string

from django.core.exceptions import ValidationError
from django.core.validators import validate_slug
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.html import escape

from .models import Paste
from .modules.markdown import compile_md
from .modules.utils import hash_sha512


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
    if not request.POST:  # if it is just viewing the page
        return render(request, "myapp/create.html")
    else:
        # prepare
        content = request.POST['content'].strip()
        paste_url = request.POST['paste_url'].strip()
        if not paste_url:
            paste_url = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

        # validate
        error_messages = []
        if len(content) > 262144:
            error_messages.append(f"contents is too long ({len(content)} > 262144)")
        elif len(content) < 1:
            error_messages.append(f"contents are too short ({len(content)} < 1)")
        if len(paste_url) > 256:
            error_messages.append(f"paste url is too long ({len(paste_url)} > 256)")
        if len(request.POST['edit_code']) > 512:
            error_messages.append(f"edit code is too long ({len(request.POST['edit_code'])} > 512)")
        elif len(request.POST['edit_code']) < 1:
            error_messages.append(f"edit code is too short ({len(request.POST['edit_code'])} < 1)")
        if Paste.objects.filter(url_name=paste_url).exists():
            error_messages.append(f"such url is already taken")
        try: validate_slug(paste_url)  # NOQA E702
        except ValidationError:
            error_messages.append("url must only contain letters, numbers, hyphens and underscores")
        if error_messages:
            return render(request, "myapp/create.html", {
                'content': content,
                'paste_url': request.POST['paste_url'],
                'error_messages': error_messages
            })

        edit_code = hash_sha512(request.POST['edit_code'])

        # create the paste
        compiled = compile_md(content)

        creation_date = datetime.today()
        paste = Paste(
            content=content,
            url_name=paste_url,
            edit_code=edit_code,
            compiled=compiled,
            creation_date=creation_date,
            edited_date=creation_date
        )

        paste.save()

        # redirect user to the `view` page
        return HttpResponseRedirect(reverse("myapp:view", args=(paste_url,)))


def edit(request, paste_url: str):
    paste = get_object_or_404(Paste, url_name=paste_url)
    if not request.POST:  # if it is just viewing the page
        return render(request, "myapp/edit.html", {
            'new_content': paste.content,
            'current_url': paste_url
        })
    else:
        # prepare
        new_content = request.POST['new_content'].strip()
        new_paste_url = request.POST['new_paste_url'].strip()

        entered_edit_code = hash_sha512(request.POST['edit_code'])

        # validate
        error_messages = []
        if entered_edit_code != paste.edit_code:
            error_messages.append(f"invalid edit code")
        if len(new_content) > 262144:
            error_messages.append(f"new contents are too long ({len(new_content)} > 262144)")
        elif len(new_content) < 1:
            error_messages.append(f"new contents are too short ({len(new_content)} < 1)")
        if len(new_paste_url) > 256:
            error_messages.append(f"new paste url is too long ({len(new_paste_url)} > 256)")
        if len(request.POST['new_edit_code']) > 512:
            error_messages.append(f"new edit code is too long ({len(request.POST['new_edit_code'])} > 512)")
        if new_paste_url and Paste.objects.filter(url_name=new_paste_url).exists():
            error_messages.append(f"such new url is already taken")
        if new_paste_url:
            try:
                validate_slug(new_paste_url)
            except ValidationError:
                error_messages.append("new url must only contain letters, numbers, hyphens and underscores")
        if error_messages:
            return render(request, "myapp/edit.html", {
                'new_content': new_content,
                'new_paste_url': request.POST['new_paste_url'],
                'error_messages': error_messages,
                'current_url': paste_url
            })

        # edit the paste
        paste.content = new_content
        if new_paste_url:
            paste.url_name = new_paste_url
        if request.POST['new_edit_code']:
            paste.edit_code = hash_sha512(request.POST['new_edit_code'])
        paste.edited_date = datetime.today()

        paste.compiled = compile_md(escape(new_content))

        paste.save()

        # redirect user to the `view` page
        return HttpResponseRedirect(reverse("myapp:view", args=(new_paste_url if new_paste_url else paste_url,)))


# error page handlers

def page_not_found(request, exception=None):
    return render(request, "myapp/error.html", {'error_code': 404})


def server_error(request, exception=None):
    return render(request, "myapp/error.html", {'error_code': 500})


def bad_request(request, exception=None):
    return render(request, "myapp/error.html", {'error_code': 400})
