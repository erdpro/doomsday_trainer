import requests

from flask import redirect, render_template, session
from functools import wraps


def apology(message, code=400):
    return render_template("apology.html", top=code, message=message)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/homepage")
        return f(*args, **kwargs)

    return decorated_function