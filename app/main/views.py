from flask import current_app
from flask import flash
from flask import make_response
from flask import redirect, url_for, render_template, abort
from flask import request
from flask_login import current_user
from flask_login import login_required

from app.decorators import admin_required, permission_required
from . import main
from app import db
from .forms import EditProfileForm, EditProfileAdminForm, PostForm
from ..models import User, Role, Post, Permission, Follow


@main.route('/', methods=['POST', 'GET'])
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.body.data, author_id=current_user.id)
        db.session.add(post)
        flash('post successfully')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts_query
    else:
        query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts,
                           pagination=pagination, show_followed=show_followed)


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp


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


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    post = Post.query.get_or_404(int(id))
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash('post already updated')
        return redirect(url_for('.post', id=id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form, post=post)


@main.route('/delete_post/<int:id>')
def delete_post(id):
    post = Post.query.get(int(id))
    if post is None:
        flash("post doesn't exist")
    else:
        db.session.delete(post)
        flash('delete successfully')
    return redirect(url_for('main.index'))


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    current_user.follow(user)
    flash('followed %s' % username)
    return redirect(url_for('main.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    current_user.unfollow(user)
    flash('unfollowed %s' % username)
    return redirect(url_for('main.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user')
        return redirect(url_for('.index'))
    pagination = user.followers.order_by(Follow.timestamp.desc()).paginate(
        page=request.args.get('page', 1, type=int), per_page=10, error_out=False)
    followers = [{'user': item.follower, 'timestamp': item.timestamp} for item in pagination.items]
    return render_template('followers.html', followers=followers, user=user, pagination=pagination)


@main.route('/is_followed_by/<username>')
def follow_ones(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user')
        return redirect(url_for('.index'))
    pagination = user.followed.order_by(Follow.timestamp.desc()).paginate(
        page=request.args.get('page', 1, type=int), per_page=10, error_out=False)
    followers = [{'user': item.followed, 'timestamp': item.timestamp} for item in pagination.items]
    return render_template('followed_ones.html', followers=followers, user=user, pagination=pagination)
