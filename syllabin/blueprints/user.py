import os
from flask import render_template, flash, redirect, request, url_for, Blueprint, current_app
from flask_login import login_required, current_user

from syllabin.components import db, avatars, csrf
from syllabin.forms.user import UploadAvatarForm, CropAvatarForm, ChangePasswordForm
from syllabin.models import Subscription


user_bp = Blueprint('user', __name__)


@user_bp.route('/notification_token', methods=['POST'])
@login_required
@csrf.exempt
def notification_token():
    if request.is_json:
        data = request.json
        subscription = Subscription.query.filter_by(subscription_info=data).first()
        if not subscription:
            if current_user.group:
                subscription = Subscription(group_id=current_user.group.id, subscription_info=data)
            else:
                subscription = Subscription(subscription_info=data)
            db.session.add(subscription)
            db.session.commit()
    return 'ok'


@user_bp.route('/settings/avatar')
@login_required
def change_avatar():
    return render_template('settings/change_avatar.html')


@user_bp.route('/settings/avatar/upload', methods=['POST'])
@login_required
def upload_avatar():
    form = UploadAvatarForm()
    if form.validate_on_submit():
        image = form.image.data
        filename = avatars.save_avatar(image)
        if current_user.pfp_raw:
            os.remove(os.path.join(current_app.config['AVATARS_SAVE_PATH'], current_user.pfp_raw))
        current_user.pfp_raw = filename
        db.session.commit()
        flash('Image uploaded, please crop.', 'success')
    return redirect(url_for('.change_avatar'))


@user_bp.route('/settings/avatar/crop', methods=['POST'])
@login_required
def crop_avatar():
    form = CropAvatarForm()
    if form.validate_on_submit():
        x = form.x.data
        y = form.y.data
        w = form.w.data
        h = form.h.data
        filenames = avatars.crop_avatar(current_user.pfp_raw, x, y, w, h)
        os.remove(os.path.join(current_app.config['AVATARS_SAVE_PATH'], current_user.pfp_s))
        os.remove(os.path.join(current_app.config['AVATARS_SAVE_PATH'], current_user.pfp_m))
        os.remove(os.path.join(current_app.config['AVATARS_SAVE_PATH'], current_user.pfp_l))
        current_user.pfp_s = filenames[0]
        current_user.pfp_m = filenames[1]
        current_user.pfp_l = filenames[2]
        db.session.commit()
        flash('Avatar updated.', 'success')
    return redirect(url_for('.change_avatar'))


@user_bp.route('/settings/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.validate_password(form.old_password.data):
            current_user.set_password(form.password.data)
            db.session.commit()
            flash('Password updated.', 'success')
            return redirect(url_for('.change_password', username=current_user.username))
        else:
            flash('Old password is incorrect.', 'warning')
    return render_template('settings/change_password.html', form=form)
