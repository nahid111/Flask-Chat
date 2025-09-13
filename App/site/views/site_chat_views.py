import functools
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from flask_socketio import disconnect, emit
from sqlalchemy import or_, desc
from App import db, socketio
from Helpers import row2dict
from Models.models import User, Conversation, Message


site_chat_views_module = Blueprint(
    'site_chat', __name__, template_folder='../templates'
)


# ==========================================================================================
#                               Index Routes & Views
# ==========================================================================================
@site_chat_views_module.route('/chat')
@login_required
def chat():
    return render_template('site/chat.html.jinja2')


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#                                       Ajax Routes
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


# ====================================================
#           Handle Search Autocomplete
# ====================================================
@site_chat_views_module.route('/chat/search_user')
@login_required
def search_auto():
    key_words = request.args.get('search', 0, type=str)
    users = User.query.filter(User.username.like('%' + key_words + '%')).all()
    users_list = []
    for x in users:
        d = row2dict(x)
        users_list.append(d)
    return jsonify(users=users_list)


# ====================================================
#            get a particular user's info
# ====================================================
@site_chat_views_module.route('/chat/get_user')
@login_required
def get_user():
    uid = request.args.get('user_id')
    user = User.query.get(uid)
    return jsonify(row2dict(user))


# ====================================================
#          Update Conversation with an user
# ====================================================
@site_chat_views_module.route('/chat/update_conversations_list')
@login_required
def update_conversations_list():
    conversations = Conversation.query.filter(
        or_(
            Conversation.started_by == current_user.id,
            Conversation.started_with == current_user.id,
        )
    ).all()

    json_list = []
    for conv in conversations:
        # get_rcvr
        if conv.started_by != current_user.id:
            rcvr = User.query.get(conv.started_by)
        else:
            rcvr = User.query.get(conv.started_with)
        message = conv.messages.order_by(desc(Message.id)).first()
        r = {
            'conv_id': conv.id,
            'rcvr_id': rcvr.id,
            'rcvr_name': rcvr.username,
            'rcvr_avatar': rcvr.avatar,
            'last_msg': message.message,
            'last_msg_time': message.created_at,
        }
        json_list.append(r)

    return jsonify(json_list)


# ====================================================
#           load Conversation with an user
# ====================================================
@site_chat_views_module.route('/chat/load_conversation')
@login_required
def load_conversation():
    current_user_id = request.args.get('current_user_id')
    other_user_id = request.args.get('other_user_id')

    row = Conversation.query.filter(
        Conversation.started_by == current_user_id,
        Conversation.started_with == other_user_id,
    ).first()
    if row:
        conversation = row
    else:
        conversation = Conversation.query.filter(
            Conversation.started_by == other_user_id,
            Conversation.started_with == current_user_id,
        ).first()

    if conversation:
        json_dict = {'conv_found': True, 'conv_id': conversation.id}
    else:
        json_dict = {'conv_found': False, 'conv_id': None}

    return jsonify(json_dict)


# =======================================================
# load Messages of a particular Conversation with an user
# =======================================================
@site_chat_views_module.route('/chat/load_messages')
@login_required
def load_messages():
    conv_id = request.args.get('conversation_id')
    the_conv = Conversation.query.get(conv_id)
    messages = the_conv.messages
    messages_list = [row2dict(m) for m in messages]
    return jsonify(messages_list)


# ====================================================
#               Save a message to DB
# ====================================================
@site_chat_views_module.route('/chat/save_message')
@login_required
def save_message():
    the_msg = request.args.get('the_msg')
    sender_id = request.args.get('sender_id')
    receiver_id = request.args.get('receiver_id')

    # check if conversation exists
    row = Conversation.query.filter(
        Conversation.started_by == sender_id,
        Conversation.started_with == receiver_id,
    ).first()
    if row:
        conversation = row
    else:
        conversation = Conversation.query.filter(
            Conversation.started_by == receiver_id,
            Conversation.started_with == sender_id,
        ).first()

    if not conversation:
        ttl = 'Untitled'
        conversation = Conversation(
            title=ttl, started_by=sender_id, started_with=receiver_id
        )
        db.session.add(conversation)
        db.session.commit()

    # save the msg to DB
    new_msg = Message(
        message=the_msg,
        sent_from=sender_id,
        sent_to=receiver_id,
        conversation=conversation,
    )
    db.session.add(new_msg)
    db.session.commit()

    return jsonify(row2dict(new_msg))


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#                                       Socket Routes
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


# *****************************************************
#      alternative decorator for @login_required
# *****************************************************
def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)

    return wrapped


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
#               update sid on connect
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
@socketio.on('update sid request')
@authenticated_only
def update_sid_event():
    if request.sid != current_user.socketio_session_id:
        current_user.socketio_session_id = request.sid
        db.session.commit()


# ====================================================
#       get msg from Sender and give to receiver
# ====================================================
# @socketio.on('event_name')
@socketio.on('send request')
@authenticated_only
def receive_message_event(msg_JSON):
    # get receiver
    receiver = User.query.get(msg_JSON['sent_to'])
    receiver_sid = receiver.socketio_session_id
    print(msg_JSON['message'], 'Sent to', receiver_sid)

    # sending out the message
    # socketio.emit('event_name', json, room=receiver_socket_id)
    socketio.emit('receive response', msg_JSON, room=receiver_sid)


# ====================================================
#       Socket.IO Broadcast Online Status
# ====================================================
@socketio.on('broadcast online request')
def broadcast_online_event():
    data = {'status': 'online', 'user_id': current_user.id}
    emit('broadcast online response', data, broadcast=True)
