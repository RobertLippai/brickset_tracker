from flask_login import current_user
from functools import wraps
from flask import abort

def editor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'editor':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def api_editor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401, "Editor role required!")
        return f(*args, **kwargs)
    return decorated_function