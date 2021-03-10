from sqlalchemy.exc import IntegrityError

from syllabin.components import db
from syllabin.models import User, Group


def add_admin():
    admin = User(username = 'Ilya_MZP',
            name='[REDACTED]',
            active = True)
    admin.set_role('Admin')
    admin.set_password('1q2w3e4r5t6y')
    db.session.add(admin)
    db.session.commit()
