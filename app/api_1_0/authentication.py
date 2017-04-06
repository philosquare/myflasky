from flask import g, abort, jsonify
from flask_httpauth import HTTPBasicAuth

from . import api
from app.models import AnonymousUser, User

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email_or_token, password):
    if email_or_token == '':
        g.current_user = AnonymousUser()
        return True
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = None
    return user.verify_password(password)


@auth.error_handler
def auth_error():
    abort(401, 'Invalid credentials')


@api.before_request
@auth.login_required
def before_request():
    if not g.current_user.is_anonymous and \
            not g.current_user.confirmed:
        abort(403, 'Unconfirmed account')


@api.route('/token')
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        abort(401, 'Invalid credentials')
    return jsonify({'token': g.current_user.generate_auth_token(expiration=3600),
                    'expiration': 3600})
