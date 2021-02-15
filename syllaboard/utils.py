import os
import uuid
import calendar
import operator
from datetime import datetime, timedelta, date

try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin

import PIL
from PIL import Image
from flask import current_app, request, url_for, redirect, flash
from flask_login import current_user
from itsdangerous import BadSignature, SignatureExpired
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from syllaboard.components import db
from syllaboard.models import User, Group, Subject, Room, Professor, Timetable
"""
from syllaboard.settings import Operations


def generate_token(user, operation, expire_in=None, **kwargs):
    s = Serializer(current_app.config['SECRET_KEY'], expire_in)

    data = {'id': user.id, 'operation': operation}
    data.update(**kwargs)
    return s.dumps(data)


def validate_token(user, token, operation, new_password=None):
    s = Serializer(current_app.config['SECRET_KEY'])

    try:
        data = s.loads(token)
    except (SignatureExpired, BadSignature):
        return False

    if operation != data.get('operation') or user.id != data.get('id'):
        return False

    if operation == Operations.CONFIRM:
        user.confirmed = True
    elif operation == Operations.RESET_PASSWORD:
        user.set_password(new_password)
    elif operation == Operations.CHANGE_EMAIL:
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if User.query.filter_by(email=new_email).first() is not None:
            return False
        user.email = new_email
    else:
        return False

    db.session.commit()
    return True


def rename_image(old_filename):
    ext = os.path.splitext(old_filename)[1]
    new_filename = uuid.uuid4().hex + ext
    return new_filename


def resize_image(image, filename, base_width):
    filename, ext = os.path.splitext(filename)
    img = Image.open(image)
    if img.size[0] <= base_width:
        return filename + ext
    w_percent = (base_width / float(img.size[0]))
    h_size = int((float(img.size[1]) * float(w_percent)))
    img = img.resize((base_width, h_size), PIL.Image.ANTIALIAS)

    filename += current_app.config['ALBUMY_PHOTO_SUFFIX'][base_width] + ext
    img.save(os.path.join(current_app.config['ALBUMY_UPLOAD_PATH'], filename), optimize=True, quality=85)
    return filename
"""


def getFirstDay(dt, d_months=0, d_years=0):
    # d_years, d_months are "deltas" to apply to dt
    y, m = dt.year + d_years, dt.month + d_months
    a, m = divmod(m-1, 12)
    return datetime(y+a, m+1, 1)


def isWeekday(dt=date.today()):
    int_day_of_week = dt.weekday()
    day_of_week = calendar.day_name[int_day_of_week]
    if day_of_week not in ['Saturday','Sunday']:
        return True
    else:
        return False


def getCurrentDay(dt=date.today()):
    int_day_of_week = dt.weekday()
    return calendar.day_name[int_day_of_week]


def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)


def getFirstWorkingDayOfMonth(dt=date.today()):
    first_day_of_month = getFirstDay(dt)
    seventh_day_of_month = first_day_of_month + timedelta(days=6)
    for d in daterange(first_day_of_month, seventh_day_of_month):
        if isWeekday(d):
            return d.date()
        else:
            continue


def getCurrentWeek(dt=date.today()):
    if dt.month > 8:
        start = 9
    else:
        start = 2
    first_working_day_of_month = getFirstWorkingDayOfMonth(datetime(dt.year, start, dt.day))
    return dt.isocalendar()[1] - first_working_day_of_month.isocalendar()[1] + 1


def getTodayEntries():
    current_week = getCurrentWeek()
    current_day = getCurrentDay()
    user_group = current_user.group
    if current_user.is_admin or user_group is None:
        today_table_entries = Timetable.query.filter_by(weekday=current_day).all()
    else:
        today_table_entries = Timetable.query.filter_by(weekday=current_day, group_id=user_group.id).all()
    current_entries = []
    for today_table_entry in today_table_entries:
        if today_table_entry.week_nums.count(str(current_week)):
            for lesson in today_table_entry.lesson_nums:
                current_entries.append([today_table_entry, int(lesson)])
    return sorted(current_entries, key=lambda x: x[1])


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


def redirect_back(default='main.index', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))
