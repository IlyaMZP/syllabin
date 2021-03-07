import datetime
from flask import render_template, flash, redirect, request, url_for, Blueprint
from flask_login import login_required, current_user
from flask_wtf import FlaskForm

from syllabin.components import db
from syllabin.models import Group, Subject, Room, Professor, Timetable, User
from syllabin.decorators import headman_required
from syllabin.utils import getCurrentWeek
from syllabin.notifications import notify_group

dash_bp = Blueprint('dash', __name__)


@dash_bp.route('')
@login_required
@headman_required
def index():
    groups = Group.query.all()
    rooms = Room.query.all()
    subjects = Subject.query.all()
    professors = Professor.query.all()
    if current_user.is_admin:
        timetable = Timetable.query.all()
    else:
        timetable = Timetable.query.filter_by(group_id=current_user.group.id).all()
    if current_user.is_admin:
        users = User.query.all()
    else:
        users = []
    return render_template('dashboard/index.html', users=users, groups=groups, rooms=rooms, subjects=subjects, timetable=timetable, professors=professors)


@dash_bp.route('/add_entry', methods=['GET', 'POST'])
@login_required
@headman_required
def add_entry():
    form = FlaskForm()
    if form.validate_on_submit():
        weeks = request.form.getlist('weeks[]')
        if not weeks:
            date_str = request.form['date']
            if date_str:
                weeks = [ str(getCurrentWeek(datetime.datetime.strptime(date_str, '%Y-%m-%d'))) ]
        lessons = request.form.getlist('lessons[]')
        subject = request.form['subject']
        room = request.form['room']
        day = request.form['day']
        professor = request.form['professor']
        try:
            group = request.form['group']
        except:
            group = current_user.group.name
        if all([weeks, lessons, day, subject, room, professor]):
            group_id = Group.query.filter_by(name=group).first()
            subject_id = Subject.query.filter_by(name=subject).first()
            room_id = Room.query.filter_by(name=room).first()
            professor_id = Professor.query.filter_by(name=professor).first()
            if not group_id:
                group_id = Group.query.filter_by(name=group).first()
                flash('No such group. Create a new group first.', 'warning')
                return redirect(url_for('dash.add_entry'))  # TODO: Redirect to create group page
            if not professor_id:
                professor_id = Professor(name=professor)
                db.session.add(professor_id)
            if not room_id:
                room_id = Room(name=room)
                db.session.add(room_id)
            if not subject_id:
                subject_id = Subject(name=subject)
                db.session.add(subject_id)
            db.session.commit()
            entry = Timetable(weekday=day, week_nums=weeks, lesson_nums=lessons, room_id=room_id.id, subj_id=subject_id.id, group_id=group_id.id, prof_id=professor_id.id)
            db.session.add(entry)
            db.session.commit()
            flash('Success.', 'info')
        else:
            flash('Some fields were empty.', 'warning')
        return redirect(url_for('dash.add_entry'))
    return render_template('dashboard/add_entry.html', form=form, groups=Group.query.all())


@dash_bp.route('/edit_entry/<int:entry_id>', methods=['GET', 'POST'])
@login_required
@headman_required
def edit_entry(entry_id):
    form = FlaskForm()
    entry = Timetable.query.get(entry_id)
    if entry is None:
        flash('Entry does not exixt.', 'warning')
        return redirect(url_for('dash.index'))
    if form.validate_on_submit():
        weeks = request.form.getlist('weeks[]')
        lessons = request.form.getlist('lessons[]')
        subject = request.form['subject']
        room = request.form['room']
        day = request.form['day']
        professor = request.form['professor']
        group = request.form.get('group', current_user.group.name)
        if all([weeks, lessons, day, subject, room, professor, group]):
            group_id = Group.query.filter_by(name=group).first()
            if group_id is None:
                flash("Group doesn't exist.", 'warning')
                return redirect(url_for('dash.edit_entry', entry_id=entry_id))
            subject_id = Subject.query.filter_by(name=subject).first()
            room_id = Room.query.filter_by(name=room).first()
            professor_id = Professor.query.filter_by(name=professor).first()
            if not professor_id:
                professor_id = Professor(name=professor)
                db.session.add(professor_id)
            if not room_id:
                room_id = Room(name=room)
                db.session.add(room_id)
            if not subject_id:
                subject_id = Subject(name=subject)
                db.session.add(subject_id)
            try:
                db.session.commit()
            except:
                db.session.rollback()
                flash('Unknown error.', 'warning')
                pass
            entry.prof_id = professor_id.id
            entry.subj_id = subject_id.id
            entry.group_id = group_id.id
            entry.room_id = room_id.id
            entry.lesson_nums = lessons
            entry.week_nums = weeks
            entry.weekday = day
            try:
                db.session.commit()
                flash('Success.', 'info')
                return redirect(url_for('dash.manage_entries'))
            except:
                db.session.rollback()
                flash('Unknown error.', 'warning')
                pass
    return render_template('dashboard/edit_entry.html', form=form, entry=entry, groups=Group.query.all())


@dash_bp.route('/manage_entries')
@login_required
@headman_required
def manage_entries():
    if current_user.is_admin:
        entries = Timetable.query.all()
    else:
        entries = Timetable.query.filter_by(group_id=current_user.group.id).all()
    return render_template('dashboard/manage_entries.html', entries=entries)


@dash_bp.route('/delete_entry/<int:entry_id>')
@login_required
def delete_entry(entry_id):
    to_delete = Timetable.query.get(entry_id)
    if to_delete:
        db.session.delete(to_delete)
        db.session.commit()
        flash('Success.', 'info')
    return redirect(url_for('dash.manage_entries'))


@dash_bp.route('/manage_subjects')
@login_required
@headman_required
def manage_subjects():
    subjects = Subject.query.all()
    return render_template('dashboard/manage_subjects.html', subjects=subjects)


@dash_bp.route('/delete_subject/<int:subject_id>')
@login_required
@headman_required
def delete_subject(subject_id):
    if not current_user.is_admin:
        used = Timetable.query.filter(Timetable.subj_id==subject_id, Timetable.group_id != current_user.group.id).first()
        if used:
            flash('This item is used by another group and cannot be deleted.', 'danger')
            return redirect(url_for('dash.manage_subjects'))
    to_delete = Subject.query.get(subject_id)
    if to_delete:
        db.session.delete(to_delete)
        db.session.commit()
        flash('Success.', 'info')
    return redirect(url_for('dash.manage_subjects'))


@dash_bp.route('/edit_subject/<int:subject_id>', methods=['GET', 'POST'])
@login_required
@headman_required
def edit_subject(subject_id):
    form = FlaskForm()
    to_edit = Subject.query.get(subject_id)
    if form.validate_on_submit():
        subject_name = request.form['subject']
        if not subject_name:
            flash('Name cannot be empty.', 'warning')
            return redirect(url_for('dash.manage_subjects'))
        if not current_user.is_admin:
            used = Timetable.query.filter(Timetable.subj_id==subject_id, Timetable.group_id!=current_user.group.id).first()
            if used:
                flash('This item is used by another group and cannot be edited.', 'danger')
                return redirect(url_for('dash.manage_subjects'))
        subject_id = Subject.query.filter_by(name=subject_name).first()
        if not subject_id:
            to_edit.name = subject_name
            db.session.commit()
        flash('Success.', 'info')
        return redirect(url_for('dash.manage_subjects'))
    return render_template('dashboard/edit_subject.html', form=form, subject=to_edit)


@dash_bp.route('/manage_professors')
@login_required
@headman_required
def manage_professors():
    professors = Professor.query.all()
    return render_template('dashboard/manage_professors.html', professors=professors)


@dash_bp.route('/delete_professor/<int:professor_id>')
@login_required
@headman_required
def delete_professor(professor_id):
    if not current_user.is_admin:
        used = Timetable.query.filter(Timetable.prof_id==professor_id, Timetable.group_id!=current_user.group.id).first()
        if used:
            flash('This item is used by another group and cannot be deleted.', 'danger')
            return redirect(url_for('dash.manage_professors'))
    to_delete = Professor.query.get(professor_id)
    if to_delete:
        db.session.delete(to_delete)
        db.session.commit()
        flash('Success.', 'info')
    return redirect(url_for('dash.manage_professors'))


@dash_bp.route('/edit_professor/<int:professor_id>', methods=['GET', 'POST'])
@login_required
@headman_required
def edit_professor(professor_id):
    form = FlaskForm()
    to_edit = Professor.query.get(professor_id)
    if form.validate_on_submit():
        professor_name = request.form['professor']
        if not professor_name:
            flash('Name cannot be empty.', 'warning')
            return redirect(url_for('dash.manage_professors'))
        if not current_user.is_admin:
            used = Timetable.query.filter(Timetable.prof_id==professor_id, Timetable.group_id!=current_user.group.id).first()
            if used:
                flash('This item is used by another group and cannot be edited.', 'danger')
                return redirect(url_for('dash.manage_professors'))
        professor_id = Professor.query.filter_by(name=professor_name).first()
        if not professor_id:
            to_edit.name = professor_name
            db.session.commit()
        flash('Success.', 'info')
        return redirect(url_for('dash.manage_professors'))
    return render_template('dashboard/edit_professor.html', form=form, professor=to_edit)


@dash_bp.route('/manage_rooms')
@login_required
@headman_required
def manage_rooms():
    rooms = Room.query.all()
    return render_template('dashboard/manage_rooms.html', rooms=rooms)


@dash_bp.route('/delete_room/<int:room_id>')
@login_required
@headman_required
def delete_room(room_id):
    if not current_user.is_admin:
        used = Timetable.query.filter(Timetable.room_id==room_id, Timetable.group_id!=current_user.group.id).first()
        if used:
            flash('This item is used by another group and cannot be deleted.', 'danger')
            return redirect(url_for('dash.manage_rooms'))
    to_delete = Room.query.get(room_id)
    if to_delete:
        db.session.delete(to_delete)
        db.session.commit()
        flash('Success.', 'info')
    return redirect(url_for('dash.manage_rooms'))


@dash_bp.route('/edit_room/<int:room_id>', methods=['GET', 'POST'])
@login_required
@headman_required
def edit_room(room_id):
    form = FlaskForm()
    to_edit = Room.query.get(room_id)
    if form.validate_on_submit():
        room_name = request.form['room']
        if not room_name:
            flash('Name cannot be empty.', 'warning')
            return redirect(url_for('dash.manage_rooms'))
        if not current_user.is_admin:
            used = Timetable.query.filter(Timetable.room_id==room_id, Timetable.group_id!=current_user.group.id).first()
            if used:
                flash('This item is used by another group and cannot be edited.', 'danger')
                return redirect(url_for('dash.manage_rooms'))
        room_id = Room.query.filter_by(name=room_name).first()
        if not room_id:
            to_edit.name = room_name
            db.session.commit()
        flash('Success.', 'info')
        return redirect(url_for('dash.manage_rooms'))
    return render_template('dashboard/edit_room.html', form=form, room=to_edit)


@dash_bp.route('/send_notification', methods=['GET', 'POST'])
@login_required
@headman_required
def send_notification():
    groups = Group.query.all()
    form = FlaskForm()
    if form.validate_on_submit():
        group = request.form['group']
        text = request.form['notification_text']
        if group and current_user.is_admin:
            notify_group(text, group)
        else:
            notify_group(text)
        flash('Success.', 'info')
    return render_template('dashboard/notify_group.html', form=form, groups=groups)
