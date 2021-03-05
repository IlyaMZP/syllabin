import os
import sys

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class BaseConfig(object):
    SECRET_KEY = 'CHANGE_ME!'
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SYLLABIN_ADMIN_EMAIL = 'ilya@mzp.icu'
    SYLLABIN_UPLOAD_PATH = os.path.join(basedir, 'uploads')
    SYLLABIN_ALLOWED_IMAGE_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']
    SESSION_COOKIE_SAMESITE = 'Strict'
    SESSION_COOKIE_SECURE = True
    SYLLABIN_DOMAIN_NAME = 'mzp.icu'
    MAX_CONTENT_LENGTH = 3 * 1024 * 1024
    AVATARS_SAVE_PATH = os.path.join(SYLLABIN_UPLOAD_PATH, 'avatars')
    AVATARS_SIZE_TUPLE = (24, 100, 200)
    AVATARS_CROP_BASE_WIDTH = 320
    SYLLABIN_PUSH_PRIVATE_KEY = "7EOmZ05femDYbUH_6sx3ySEytPlo9MW3s0YgkvJio1k"
    SYLLABIN_DOMAIN_NAME = 'syllabin.mzp.icu'


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, 'data-dev.db')


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', "sqlite:///" + os.path.join(basedir, 'data.db'))


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}

