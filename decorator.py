from functools import wraps
from flask import redirect, session


def handle_session(f):
    """ Decorate function """

    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("username") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return wrapper