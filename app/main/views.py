from datetime import datetime

from flask import flash
from flask import session, current_app, redirect, url_for, render_template, abort
from flask_login import current_user
from flask_login import login_required

from app.decorators import admin_required
from . import main
from app import db
from app.email import send_email
from .forms import NameForm, EditProfileForm, EditProfileAdminForm
from ..models import User, Role


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


@main.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('you have edit your profile')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit_profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get(int(id))
    form = EditProfileAdminForm(user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.name = form.name.data
        user.about_me = form.about_me.data
        user.confirmed = form.confirmed.data
        user.location = form.location.data
        user.role = Role.query.get(int(form.role.data))
        db.session.add(user)
        flash('change profile successfully')
        return redirect(url_for('.user', username=user.username))
    form.username.data = user.username
    form.email.data = user.email
    form.name.data = user.name
    form.about_me.data = user.about_me
    form.confirmed.data = user.confirmed
    form.location.data = user.location
    form.role.data = user.role_id
    return render_template('edit_profile.html', form=form, user=user)
