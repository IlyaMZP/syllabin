import os
import uuid
import calendar
import operator
from datetime import datetime, timedelta, date

try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin

from flask import current_app, request, url_for, redirect, flash
from flask_login import current_user

from syllabin.components import db
from syllabin.models import User, Group, Subject, Room, Professor, Timetable


def getFirstWeekDay(dt):
    return dt - timedelta(days=dt.weekday())


def getFirstMonthDay(dt, d_months=0, d_years=0):
    y, m = dt.year + d_years, dt.month + d_months
    a, m = divmod(m-1, 12)
    return datetime(y+a, m+1, 1)


def isWeekday(dt):
    int_day_of_week = dt.weekday()
    day_of_week = calendar.day_name[int_day_of_week]
    if day_of_week not in ['Saturday','Sunday']:
        return True
    else:
        return False


def getCurrentDay(dt):
    int_day_of_week = dt.weekday()
    return calendar.day_name[int_day_of_week]


def getMondayForWeek(week):
    dt = date.today()
    if dt.month > 8:
        start = 9
    else:
        start = 2
    first = date(dt.year, start, 1)
    base = 1 if first.isocalendar()[1] == 1 else 8
    return first + timedelta(days=base - first.isocalendar()[2] + 7 * (week - 1))


def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)


def getFirstWorkingDayOfMonth(dt):
    first_day_of_month = getFirstMonthDay(dt)
    seventh_day_of_month = first_day_of_month + timedelta(days=6)
    for d in daterange(first_day_of_month, seventh_day_of_month):
        if isWeekday(d):
            return d.date()
        else:
            continue


def getCurrentWeek(dt):
    if dt.month > 8:
        start = 9
    else:
        start = 2
    first_working_day_of_month = getFirstWorkingDayOfMonth(datetime(dt.year, start, 1))
    return dt.isocalendar()[1] - first_working_day_of_month.isocalendar()[1] + 1


def getDayEntries(dt):
    current_week = getCurrentWeek(dt)
    current_day = getCurrentDay(dt)
    if current_user.is_admin:
        user_group = None
    else:
        user_group = current_user.group
    return getEntriesHelper(current_day, current_week, user_group)


def getWeekEntries(week_num):
    week_entries = []
    if current_user.is_admin:
        user_group = None
    else:
        user_group = current_user.group
    for current_day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
        week_entries.append(getEntriesHelper(current_day, week_num, user_group))
    return week_entries


def getEntriesHelper(current_day, current_week, user_group):
    if user_group is None:
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
