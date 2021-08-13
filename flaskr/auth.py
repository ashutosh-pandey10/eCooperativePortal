import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session,url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


# Registration View
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        mobileno = request.form['mobileno']
        emailid = request.form['emailid']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Enrollment Id is required.'
        elif not password:
            error = 'Password is required.'
        elif not firstname:
            error = 'First name is required.'
        elif not lastname:
            error = 'Last name is required.'   
        elif not mobileno:
            error = 'Mobile number is required.'   

        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            db.execute(
                'INSERT INTO user (username, firstname, lastname, mobileno, emailid, password) VALUES (?, ?, ?, ?, ?, ?)',
                (username, firstname, lastname, mobileno, emailid, generate_password_hash(password))
            )            
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)
    return render_template('auth/register.html')       


# Login View
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect enrollment Id.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

# Loading the logged in user before making any requests
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


# logging out
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# for carrying out updations in blog one needs to be
# logged into the system and the flask will ensure that
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)        

    return wrapped_view # didn't get this part completely
                        # and the above part of this method as well