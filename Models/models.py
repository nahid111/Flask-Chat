from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from flask_login import UserMixin
from App import app, db


# ===========================================================================================
#                                          Chat Models
# ===========================================================================================
# One-to-Many relationship exists between Message and Conversation

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text)
    sent_from = db.Column(db.Integer)
    sent_to = db.Column(db.Integer)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow())
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)


class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(191))
    started_by = db.Column(db.Integer)
    started_with = db.Column(db.Integer)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow())
    updated_at = db.Column(db.DateTime())
    messages = db.relationship('Message', backref='conversation', lazy='dynamic')




# ===========================================================================================
#                                         Auth Models
# ===========================================================================================

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(191), unique=True)
    password = db.Column(db.String(191))
    username = db.Column(db.String(191))
    phone = db.Column(db.String(191))
    avatar = db.Column(db.String(191))
    created_at = db.Column(db.DateTime(), default=datetime.utcnow())
    verified_at = db.Column(db.DateTime())
    socketio_session_id = db.Column(db.String(191))

    def get_password_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_password_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    


