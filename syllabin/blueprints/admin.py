import uuid
from flask import render_template, flash, redirect, request, url_for, Blueprint
from flask_login import login_required, current_user
from flask_wtf import FlaskForm

from syllabin.components import db
from syllabin.models import Group, User, Role
from syllabin.decorators import admin_required


admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/manage_users')
@login_required
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)


@admin_bp.route('/create_user', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    form = FlaskForm()
    if form.validate_on_submit():
        group_name = request.form['group']
        role_name = request.form['role']
        group = Group.query.filter_by(name=group_name).first()
        uid = str(uuid.uuid4())
        if group:
            user = User(group_id=group.id, active=False, username=uid)
            user.set_role(role_name)
            db.session.add(user)
            db.session.commit()
            message = 'Success. Registration URL: https://test.mzp.icu/auth/register?id=' + uid
            flash(message, 'info')
        else:
            flash('No such group.', 'warning')
        return redirect(url_for('admin.create_user'))
    return render_template('admin/create_user.html', form=form, roles=Role.query.all(), groups=Group.query.all())



@admin_bp.route('/edit_group/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    form = FlaskForm()
    to_edit = User.query.get(user_id)
    if form.validate_on_submit():
        group_name = request.form['group']
        role_name = request.form['role']
        group_id = Group.query.filter_by(name=group_name).first()
        role_id = Role.query.filter_by(name=role_name).first()
        to_edit.group_id = group_id.id
        to_edit.role_id = role_id.id
        db.session.commit()
        flash('Success.', 'info')
        return redirect(url_for('admin.manage_users'))
    return render_template('admin/edit_user.html', form=form, user=to_edit, roles=Role.query.all(), groups=Group.query.all())


@admin_bp.route('/delete_user/<int:user_id>')
@login_required
@admin_required
def delete_user(user_id):
    to_delete = User.query.get(user_id)
    if to_delete:
        db.session.delete(to_delete)
        db.session.commit()
        flash('Success.', 'info')
    return redirect(url_for('admin.manage_users'))


@admin_bp.route('/manage_groups')
@login_required
@admin_required
def manage_groups():
    groups = Group.query.all()
    return render_template('admin/manage_groups.html', groups=groups)


@admin_bp.route('/delete_group/<int:group_id>')
@login_required
@admin_required
def delete_group(group_id):
    to_delete = Group.query.get(group_id)
    if to_delete:
        db.session.delete(to_delete)
        db.session.commit()
        flash('Success.', 'info')
    return redirect(url_for('admin.manage_groups'))


@admin_bp.route('/edit_group/<int:group_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_group(group_id):
    form = FlaskForm()
    to_edit = Group.query.get(group_id)
    if form.validate_on_submit():
        group_name = request.form['group']
        group_id = Group.query.filter_by(name=group_name).first()
        if not group_id:
            to_edit.name = group_name
            db.session.commit()
        flash('Success.', 'info')
        return redirect(url_for('admin.manage_groups'))
    return render_template('admin/edit_group.html', form=form, group=to_edit)


@admin_bp.route('/create_group', methods=['GET', 'POST'])
@login_required
@admin_required
def create_group():
    form = FlaskForm()
    if form.validate_on_submit():
        group = request.form['group']
        if group:
            group_id = Group.query.filter_by(name=group).first()
            if not group_id:
                group_id = Group(name=group)
                db.session.add(group_id)
            db.session.commit()
        flash('Success.', 'info')
        return redirect(url_for('admin.create_group'))
    return render_template('admin/create_group.html', form=form)
