from flask import render_template, flash, redirect, request, url_for, Blueprint
from flask_login import login_required, current_user

from syllaboard.components import db, avatars
from syllaboard.forms.user import UploadAvatarForm, CropAvatarForm


user_bp = Blueprint('user', __name__)


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
        current_user.pfp_s = filenames[0]
        current_user.pfp_m = filenames[1]
        current_user.pfp_l = filenames[2]
        db.session.commit()
        flash('Avatar updated.', 'success')
    return redirect(url_for('.change_avatar'))
