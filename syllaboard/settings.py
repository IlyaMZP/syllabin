import os
import sys

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class BaseConfig(object):
    SECRET_KEY = 'CHANGE_ME!'
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SYLLABOARD_ADMIN_EMAIL = 'ilya@mzp.icu'
    SYLLABOARD_SLOW_QUERY_THRESHOLD = 1
    SYLLABOARD_UPLOAD_PATH = os.path.join(basedir, 'uploads')
    SYLLABOARD_ALLOWED_IMAGE_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']
    SESSION_COOKIE_SAMESITE = 'Strict'
    SESSION_COOKIE_SECURE = True
    SYLLABOARD_DOMAIN_NAME = 'mzp.icu'
    MAX_CONTENT_LENGTH = 3 * 1024 * 1024
    AVATARS_SAVE_PATH = os.path.join(SYLLABOARD_UPLOAD_PATH, 'avatars')
    AVATARS_SIZE_TUPLE = (20, 100, 200)
    AVATARS_CROP_BASE_WIDTH = 320


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, 'data-dev.db')


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', "sqlite:///" + os.path.join(basedir, 'data.db'))


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}

