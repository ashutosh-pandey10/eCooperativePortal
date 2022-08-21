import os
import functools
from flaskr.db import get_db
from flask import (
    Blueprint, flash, current_app, g, redirect, render_template, session, request, url_for, send_from_directory
)


bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/login', methods=('POST', 'GET'))
# logging in for admin
def admin_login():
    if request.method == 'POST':
        admin_username = request.form['admin_username']
        admin_password = request.form['admin_password']
        db = get_db()
        error = None
        admn = db.execute(
            'SELECT * FROM admn WHERE admin_name = ?', (admin_username,)
        ).fetchone()

        if admn is None:
            error = 'Incorrect Admin Id.'

        elif admn['admin_password'] != admin_password :
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['admin_id'] = admn['id']
            return redirect(url_for('admin.home'))

        flash(error)

    return render_template('admin/admin_login.html') 


def admin_login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.admn is None:
            return redirect(url_for('admin.admin_login'))
        
        return view(**kwargs)        

    return wrapped_view 

# loading the logged in admin
@bp.before_app_request
def load_logged_in_admin():
    admin_id = session.get('admin_id')

    if admin_id is None:
        g.admn = None
    else:
        g.admn = get_db().execute(
            'SELECT * FROM admn WHERE id = ?', (admin_id,)
        ).fetchone()


# logging out
@bp.route('/adm_logout')
def logout():
    session.clear()
    return redirect(url_for('admin.admin_login'))


@bp.route('/home')
@admin_login_required
def home():
    db = get_db()
    placed_orders = db.execute(
        'SELECT po.id, printorder_id, f_name, file_path, file_cost, created, confirmation_received, confirmation_admin, username, firstname, lastname'
        ' FROM printorder po JOIN user u ON po.printorder_id = u.id'
        ' WHERE confirmation_received IS TRUE'
        ' ORDER BY created DESC'
    ).fetchall()
    itemorders = db.execute(
        'select a.*,u.firstname, u.lastname from itemorder a join user u on a.order_id = u.id order by a.order_created desc'
    ).fetchall()
    return render_template('admin/home.html', placed_orders=placed_orders, itemorders=itemorders)


# CONFIRMATION AND DECLINING OF ORDER

@bp.route('/<int:id>/confirmation', methods = ['POST'])
@admin_login_required
# here the parameter passed is "id" the primary key to table printorder
def confirmation(id):
    '''
    Confirms order from administrator's side
    '''
    db = get_db()
    db.execute(
        'UPDATE printorder SET confirmation_admin=? WHERE id=?',
        ("Confirmed", id)
    )
    db.commit()

    return redirect(url_for('admin.home'))


@bp.route('/<int:id>/decline', methods = ['POST'])
@admin_login_required
def decline(id):
    '''
    Declines order from administrator's side
    '''
    db = get_db()
    db.execute(
        'UPDATE printorder SET confirmation_admin=? WHERE id=?',
        ("Declined", id)
    )
    db.commit()

    return redirect(url_for('admin.home'))

#method for downloading files present in uploaded_files directory
@bp.route('/uploads/<path:filename>', methods = ['GET', 'POST'])
@admin_login_required
def download(filename):
    uploads = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])
    return send_from_directory(directory = uploads, filename = filename)
