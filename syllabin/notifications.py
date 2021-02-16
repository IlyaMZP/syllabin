import json
from threading import Thread
from pywebpush import webpush, WebPushException
from flask import current_app

from syllabin.models import User, Group, Subscription, Announcement
from syllabin.components import db


class FlaskThread(Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = current_app._get_current_object()

    def run(self):
        with self.app.app_context():
            super().run()


def notify_group(text, group_name = None):
    thread = FlaskThread(target=notify_group_thread, kwargs=dict(text=text, group_name=group_name))
    thread.daemon = True
    thread.start()


def notify_group_thread(text, group_name):
    if group_name is None:
        subscriptions = Subscription.query.all()
        announcement = Announcement(message=text)
    else:
        group = Group.query.filter_by(name=group_name).first()
        subscriptions = Subscription.query.filter_by(group_id=group.id).all()
        announcement = Announcement(message=text, group_id=group.id)
    db.session.add(announcement)
    db.session.commit()
    for subscription in subscriptions:
        if subscription.subscription_info:
            try:
	            webpush(
		            subscription_info=json.loads(subscription.subscription_info),
		            data=text,
		            vapid_private_key=current_app.config['SYLLABIN_PUSH_PRIVATE_KEY'],
		            vapid_claims={
		            "sub": "mailto:ilya@mzp.icu",
		            }
	            )
            except WebPushException as ex:
	            print("I'm sorry, Dave, but I can't do that: {}", repr(ex))
	            # Mozilla returns additional information in the body of the response.
	            if ex.response and ex.response.json():
		            extra = ex.response.json()
		            print("Remote service replied with a {}:{}, {}",
			            extra.code,
			            extra.errno,
			            extra.message
			            )
