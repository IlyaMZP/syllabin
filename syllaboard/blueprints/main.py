import os

from flask import render_template, flash, redirect, url_for, current_app, \
    send_from_directory, request, abort, Blueprint, make_response
from syllaboard.utils import getTodayEntries
from flask_login import login_required, current_user
#from sqlalchemy.sql.expression import func

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('main/index.html', entries=getTodayEntries())
    else:
        return render_template('main/index.html')


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
