from flask import current_app
from flask import flash
from flask import redirect, url_for, render_template, abort
from flask import request
from flask_login import current_user
from flask_login import login_required

from app.decorators import admin_required
from . import main
from app import db
from .forms import EditProfileForm, EditProfileAdminForm, PostForm
from ..models import User, Role, Post


@main.route('/', methods=['POST', 'GET'])
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.body.data, author_id=current_user.id)
        db.session.add(post)
        flash('post successfully')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False
    )
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts, pagination=pagination)


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
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(author=user).order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False
    )
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts, pagination=pagination)


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


@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get(int(id))
    return render_template('post.html', post=post)
