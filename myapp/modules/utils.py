import hashlib

from django.conf import settings


def hash_sha512(s: str, salted: bool = True) -> str:
    return hashlib.sha512(
        s.encode('utf-8') + settings.HASH_SALT.encode('utf-8') if salted else s.encode('utf-8')
    ).hexdigest()


