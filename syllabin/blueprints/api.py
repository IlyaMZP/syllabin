from flask import jsonify, Blueprint
from flask_login import login_required

from syllabin.components import db
from syllabin.models import User, Group, Subject, Room, Professor

api_bp = Blueprint('api', __name__)


@login_required
@api_bp.route('/roles', methods=['GET'])
def roles():
    role_names = []
    roles = Role.query.all()
    for role in roles:
        role_names.append(role.name)
    return jsonify(role_names)


@login_required
@api_bp.route('/subjects', methods=['GET'])
def subjects():
    sub_names = []
    subjects = Subject.query.all()
    for subject in subjects:
        sub_names.append(subject.name)
    return jsonify(sub_names)


@login_required
@api_bp.route('/professors', methods=['GET'])
def proffessors():
    prof_names = []
    proffessors = Professor.query.all()
    for proffessor in proffessors:
        prof_names.append(proffessor.name)
    return jsonify(prof_names)


@login_required
@api_bp.route('/rooms', methods=['GET'])
def rooms():
    room_names = []
    rooms = Room.query.all()
    for room in rooms:
        room_names.append(room.name)
    return jsonify(room_names)


@login_required
@api_bp.route('/groups', methods=['GET'])
def groups():
    group_names = []
    groups = Group.query.all()
    for group in groups:
        group_names.append(group.name)
    return jsonify(group_names)
