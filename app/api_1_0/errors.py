from flask import jsonify
from flask import abort

from app.exceptions import ValidationError
from . import api


@api.errorhandler(403)
def forbidden(e):
    response = jsonify({'error': 'forbidden', 'message': e.description})
    response.status_code = 403
    return response


@api.errorhandler(401)
def unauthorized(e):
    response = jsonify({'error': 'unauthorized', 'message': e.description})
    response.status_code = 401
    return response


@api.errorhandler(400)
def bad_request(e):
    response = jsonify({'error': 'bad request', 'message': e.description})
    response.status_code = 400
    return response


@api.errorhandler(ValidationError)
def validation_error(e):
    abort(400, e.args[0])
