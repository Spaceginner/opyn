from django.db import models


class Paste(models.Model):
    content = models.TextField()

    url_name = models.SlugField(max_length=256)

    edit_code = models.CharField(max_length=256)

    creation_date = models.DateTimeField()
    edited_date = models.DateTimeField()
