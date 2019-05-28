import re
import os
from flask import redirect, render_template, request, session
from functools import wraps

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def validate_password(password):
  if not password:
      raise ValueError('Password not provided')

  if not re.match('\d.*[A-Z]|[A-Z].*\d', password):
      raise ValueError('Password must contain 1 capital letter and 1 number')

  if len(password) < 8 or len(password) > 50:
      raise ValueError('Password must be between 8 and 50 characters')

 
def validate_username(username, db):
  if not username:
      raise ValueError('No username provided')

  if db.execute("SELECT username FROM users WHERE username = :username LIMIT 1", {"username": username}).rowcount != 0:
    raise ValueError(f'The username you provided is already in use')

  if len(username) < 5 or len(username) > 20:
    raise ValueError('Username must be between 5 and 20 characters')


def validate_email(email):
  if not email:
    raise ValueError('No email provided')

  if not re.match("[^@]+@[^@]+\.[^@]+", email):
    raise ValueError('Provided email is not an email address')


def validate_string_content(s):
    """ Validates if there are more digits than chars in a string"""

    chars = 0
    digits = 0

    for c in s:
        if c.isdigit():
            digits = digits + 1

        if c.isalpha():
            chars = chars + 1

    return True if digits > chars else False


def validate_if_user_has_review(user_id, isbn, db):
    # Validate if the actual user has already left a review
    user_has_review = True if db.execute("SELECT user_id FROM reviews WHERE user_id = :id AND isbn_number = :isbn", {"id": user_id, 
    "isbn": isbn}).fetchone() else False

    return user_has_review