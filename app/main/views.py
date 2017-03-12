from datetime import datetime
from flask import session, current_app, redirect, url_for, render_template, abort
from flask_login import login_required

from app.decorators import admin_required
from . import main
from app import db
from app.email import send_email
from .forms import NameForm
from ..models import User


@main.route('/', methods=['POST', 'GET'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        name = form.name.data
        session['name'] = name
        if User.query.filter_by(username=name).first():
            session['known'] = True
        else:
            session['known'] = False
            user = User(username=name)
            db.session.add(user)
            db.session.commit()
            if current_app.config.get('FLASKY_ADMIN'):
                send_email(to=current_app.config['FLASKY_ADMIN'],
                           subject='New User', template='mail/new_user', user=user)
        return redirect(url_for('.index'))
    return render_template('index.html', time=datetime.utcnow())


@main.route('/admin')
@login_required
@admin_required
def admin():
    return 'you are admin'


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    return render_template('user.html', user=user)
