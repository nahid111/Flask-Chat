from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
from App import db, login_manager, mail
# from App.admin.views.admin_chat_views import broadcast_offline_event, broadcast_online_event
from Models.models import User

auth_views_module = Blueprint('auth', __name__, url_prefix='/auth', template_folder='../templates')



#       the User Loader
# --------------------------------
@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    return user


# ================================================================================================
#           Auth Routes & Views
# ================================================================================================

@auth_views_module.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        usr = User.query.filter_by(email=email).first()

        if not usr or not check_password_hash(usr.password, password):
            flash(u"Incorrect Email or Password", "danger")
            return redirect(url_for('auth.login'))

        login_user(usr)
        flash(u"Successfully Signed in", "success")
        # broadcast_online_event()

        return redirect('/')

    return render_template('auth/login.html.jinja2')






@auth_views_module.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':

        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_pass = generate_password_hash(password, method='sha256')

        # check if user with same email exists
        usr = User.query.filter_by(email=email).first()

        if usr:
            flash(u"Email already exists..!", "danger")
            return redirect(url_for('auth.signup'))

        # create User
        new_usr = User(username=name, email=email, password=hashed_pass)
        # save user to DB
        db.session.add(new_usr)
        db.session.commit()

        flash(u"Successfully signed up, Sign in to continue", "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/sign-up.html.jinja2')








@auth_views_module.route("/logout")
@login_required
def logout():
    # broadcast_offline_event()
    logout_user()
    flash(u"Successfully Signed Out", "info")
    return redirect(url_for('auth.login'))












# ================================================================================================
#          Reset Password Routes & Views
# ================================================================================================

def send_password_reset_email(user):
    token = user.get_password_reset_token()
    # msg = Message("Password Reset Request from Flask-Starter-App", sender='noreply@demo.com', recipients=[user.email])
    msg = Message("Password Reset Request", recipients=[user.email])
    msg.body = f'''Visit the following link to reset your password:
    {url_for('auth.reset_password', token=token, _external=True)}
    If you did not make this request then simply ignore this email and nothing will be changed.
    '''
    mail.send(msg)


@auth_views_module.route("/forgotpassword", methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('Incorrect email!<br>Try again', "danger")
            return redirect(url_for('auth.forgot_password'))
        send_password_reset_email(user)
        flash('An email has been sent to this address with instruction to reset your password.', "info")
        return redirect(url_for('auth.login'))
    return render_template('auth/forgotpassword.html.jinja2')


@auth_views_module.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    user = User.verify_password_reset_token(token)
    if not user:
        flash('Invalid or Expired link!<br>Resubmit email', "danger")
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        password = request.form['password']
        hashed_pass = generate_password_hash(password, method='sha256')
        user.password = hashed_pass
        db.session.commit()
        flash('Your password has been updated', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/resetpassword.html.jinja2', token=token)
