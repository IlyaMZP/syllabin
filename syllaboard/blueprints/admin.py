from flask import render_template, flash, redirect, request, url_for, Blueprint
from flask_login import login_required, current_user
from flask_wtf import FlaskForm

from syllaboard.components import db
from syllaboard.models import Group, User, Role
from syllaboard.decorators import admin_required
from syllaboard.notifications import notify_group


admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/test/<string:group>')
@login_required
@admin_required
def test(group):
    notify_group("hello", group)
    return redirect(url_for('main.index'))


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
        group = request.form['group']
        role = request.form['role']
        flash('Success.', 'info')
        return redirect(url_for('admin.create_user'))
    return render_template('admin/create_user.html', form=form, roles=Role.query.all(), groups=Group.query.all())


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
