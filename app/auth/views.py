from flask import flash
from flask import request
from flask import redirect
from flask import url_for
from flask import render_template
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user

from app import db
from app.auth.forms import LoginForm, RegistrationForm, ChangePasswordForm, ResetPassword, ForgetPassword, ChangeEmail
from app.email import send_email
from app.models import User
from . import auth


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Wrong username or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['POST', 'GET'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm your account', 'auth/mail/confirm', token=token, user=user)
        flash('a confirm email has been send to your email address')
        login_user(user)
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('you has been confirmed')
    else:
        flash('invalid or expired link')
    return redirect(url_for('main.index'))


@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint[:5] != 'auth.' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main/index'))
    return render_template('auth/unconfirmed.html', user=current_user)


@auth.route('/confirm')
@login_required
def resend_confirmation():
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm account', 'auth/mail/confirm', user=current_user, token=token)
    flash('a confirm email has been send to your email address')
    return redirect(url_for('main.index'))


@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_user.password = form.new_password.data
        db.session.add(current_user)
        flash('change password successfully!')
        return redirect(url_for('main.index'))
    return render_template('auth/change_password.html', form=form)


@auth.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    form = ForgetPassword()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:
            token = user.generate_confirmation_token()
            send_email(user.email, 'Reset Your Password', 'auth/mail/reset',
                       token=token, user=user)
            flash('Please check your email to reset password')
            return redirect(url_for('main.index'))
        flash("email didn't registered")
    return render_template('auth/forget_password.html', form=form)


@auth.route('/reset_password/<token>', methods=['POST', 'GET'])
def reset_password_token(token):
    form = ResetPassword()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if user.confirm(token):
                user.password = form.new_password.data
                db.session.add(user)
                flash('password has been changed')
                return redirect(url_for('main.index'))
            else:
                flash('wrong or expired token, please reset again')
                return redirect(url_for('reset_password'))
        else:
            flash("email didn't registered")
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change_email')
@login_required
def change_email():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'change email', 'auth/mail/change_email', token=token, user=current_user)
    flash('a confirm email send to your current email')
    return redirect(url_for('main.index'))


@auth.route('/change_email/<token>', methods=['GET', 'POST'])
@login_required
def change_email_token(token):
    form = ChangeEmail()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            token = current_user.generate_email_token(email=form.email.data)
            send_email(form.email.data, 'confirm your email',
                       'auth/mail/confirm_email', token=token, user=current_user)
            flash('a confirm email has been send to your new email %s' % form.email.data)
            return redirect(url_for('main.index'))
        flash('wrong password')
    if not current_user.confirm(token):
        flash('wrong or expired token')
        return redirect(url_for('main.index'))
    return render_template('auth/change_email.html', form=form)


@auth.route('/confirm_email/<token>')
@login_required
def confirm_email(token):
    if current_user.confirm_email(token):
        flash('change email successfully')
    else:
        flash('wrong or expired token')
    return redirect(url_for('main.index'))