from flask import render_template, redirect, request, url_for, \
    flash, current_app, Response
from flask.ext.login import login_user, logout_user, login_required, \
    current_user
from . import admin
from .. import db
from ..models import Role, User, Permission
from ..decorators import admin_required
from .forms import CreateUserForm, EditUserForm

@admin.route('/')
@admin_required
def index():
    return render_template('admin/index.html')

@admin.route('/users', methods=['GET', 'POST'])
@admin_required
def users():
    '''
    Manage users - list users
    '''
    form = CreateUserForm(role=Role.query.filter_by(name='User').first().id)
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    role=Role.query.get(form.role.data),
                    password=form.password.data,
                    confirmed=form.confirmed.data,
                    name=form.name.data,
                    location=form.location.data,
                    about_me=form.about_me.data)
        db.session.add(user)
        db.session.commit()
        flash("New user has been created successfully", 'success')
        return redirect(url_for('.users'))

    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.id).paginate(
        page, per_page=current_app.config['ADMIN_ITEMS_PER_PAGE'],
        error_out=False)
    users = pagination.items
    return render_template('admin/users.html', form=form,
                           users=users, pagination=pagination)

@admin.route('/user/<int:id>', methods=['GET', 'POST'])
@admin_required
def user(id):
    '''
    View specific user
    '''
    user = User.query.get_or_404(id)
    form = EditUserForm(user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.role = Role.query.get(form.role.data)
        user.confirmed = form.confirmed.data
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash("User information has been updated successfully", 'success')
        return redirect(url_for('.user', id=id))

    form.email.data = user.email
    form.username.data = user.username
    form.role.data = user.role_id
    form.confirmed.data = user.confirmed
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('admin/user.html', form=form,
                           user=user)

@admin.route('/user/delete/<int:id>', methods=['GET', 'POST'])
@admin_required
def user_delete(id):
    '''
    Delete user
    '''
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash("User has been deleted successfully", 'success')
    return redirect(url_for('.users'))
