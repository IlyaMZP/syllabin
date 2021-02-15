from sqlalchemy.exc import IntegrityError

from syllaboard.components import db
from syllaboard.models import User, Role, Group


def add_admin():
    role = Role.query.filter_by(name='Admin').first().id
    admin = User(username = 'Ilya_MZP',
            email = 'ilya@mzp.icu',
            name='[REDACTED]',
            role_id = role)
    admin.set_password('1q2w3e4r5t6y')
    db.session.add(admin)
    db.session.commit()
