import random, string

# ================================
#       default config
# ================================
class BaseConfig(object):
    DEBUG = False
    SECRET_KEY = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    DB_HOST = 'localhost:3306'
    DB_NAME = 'your_db'
    DB_USERNAME = 'your_usr'
    DB_PASSWORD = 'yourpassword'
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://%s:%s@%s/%s" % (DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CSRF_ENABLED = True
    # Flask-Mail settings
    MAIL_SERVER = 'mail.example.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_USERNAME = 'support@example.com'
    MAIL_PASSWORD = 'password'
    MAIL_DEFAULT_SENDER = 'support@example.com'



# ================================
#       development config
# ================================
class DevelopmentConfig(BaseConfig):
    DEBUG = True






class TestConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(BaseConfig):
    DEBUG = False




