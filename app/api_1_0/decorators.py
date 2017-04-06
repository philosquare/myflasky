from functools import wraps

from flask import g, abort


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.current_user.can(permission):
                abort(403, 'Insufficient permissions')
            return f(*args, **kwargs)
        return decorated_function
    return decorator
