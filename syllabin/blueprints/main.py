import os
from datetime import date, timedelta
from flask import render_template, flash, redirect, url_for, current_app, \
    send_from_directory, request, abort, Blueprint, make_response
from flask_login import login_required, current_user
from sqlalchemy import or_

from syllabin.utils import getDayEntries, getCurrentWeek
from syllabin.models import Announcement
from syllabin.components import db
#from sqlalchemy.sql.expression import func

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        today = date.today()
        if current_user.group:
            announcements = Announcement.query.filter(or_(Announcement.group_id == current_user.group.id, Announcement.group_id == None)).all()
        else:
            announcements = Announcement.query.all()
        if announcements:
            for announcement in announcements:
                if announcement.expires.date() <= date.today():
                    db.session.delete(announcement)
                    db.session.commit()
        return render_template('main/index.html', announcements=announcements, entries=getDayEntries(today), week=getCurrentWeek(today))
    else:
        return render_template('main/index.html')


@login_required
@main_bp.route('/tomorrow')
def tomorrow():
    today = date.today() + timedelta(days=1)
    if current_user.group:
        announcements = Announcement.query.filter(or_(Announcement.group_id == current_user.group.id, Announcement.group_id == None)).all()
    else:
        announcements = Announcement.query.all()
    if announcements:
        for announcement in announcements:
            if announcement.expires.date() <= date.today():
                db.session.delete(announcement)
                db.session.commit()
    return render_template('main/index.html', announcements=announcements, entries=getDayEntries(today), week=getCurrentWeek(today))


@main_bp.route('/avatars/<path:filename>')
def get_avatar(filename):
    return send_from_directory(current_app.config['AVATARS_SAVE_PATH'], filename)


@main_bp.route('/sw.js')
def service_worker():
    response = make_response(send_from_directory('static', 'sw.js'))
    response.headers['Cache-Control'] = 'no-cache'
    return response


@main_bp.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')


@main_bp.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico')
