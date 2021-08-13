from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage

import os
from flaskr.auth import login_required
from flaskr.db import get_db
from . import plumber

from flask import current_app

bp = Blueprint('blog', __name__)

@bp.route('/')
@login_required
def index():
    db = get_db()
    printorders = db.execute(
        'SELECT po.id, printorder_id, f_name, file_path, file_cost, created, confirmation_received, confirmation_admin, username, firstname, lastname'
        ' FROM printorder po JOIN user u ON po.printorder_id = u.id'
        ' WHERE confirmation_received IS TRUE'
        ' ORDER BY created DESC'
    ).fetchall()
    itemorders = db.execute(
        'select a.*,u.firstname, u.lastname from itemorder a join user u on a.order_id = u.id order by a.order_created desc'
    )
    return render_template('blog/index.html', printorders=printorders, itemorders = itemorders)



# uploading of file
# ALLOWED_EXTENSIONS = {'pdf'}

# def allowed_file(file):
#     return '.' in file and \
#            file.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/upload', methods = ['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        try:
            f = request.files['file']
            # this line is included as the pdfs were riveously being saved in the current directory
            f.save(os.path.join(current_app.config['UPLOAD_FOLDER'], secure_filename(f.filename))) 

            fileName = secure_filename(f.filename)
            path = current_app.config['UPLOAD_FOLDER'] + str(f.filename)
            money = plumber.calculate_cost(path)

            db = get_db()
            cursor = db.execute(
                'INSERT INTO printorder (printorder_id, file_path, f_name, file_cost, confirmation_received)'
                ' VALUES (?, ?, ?, ?, ?)', 
                (g.user['id'], path, fileName, money, False)
            )
            db.commit()

            # The primary key of the inserted order is cursor.lastrowid
            lastrowid = cursor.lastrowid
            print("lastrowid value", lastrowid)
            return render_template('blog/upload.html', data = {'upload_notification': 'File ' + fileName + ' uploaded successfully', 'calculated_cost' : 'Cost for the print out : ₹'+str(money), 'id': lastrowid})

        except:
            return render_template('blog/upload.html', data = {'upload_notification': 'Invalid file! Please try again.'})    
            
    return render_template('blog/upload.html')

@bp.route('/<int:id>/confirm', methods = ['POST'])
@login_required
def confirm_order(id):
    """ 
    Confirms the printing of the file uploaded by the user. 
    """
    db = get_db()
    # Update the confirmation variable in the database. 
    db.execute(
        'UPDATE printorder SET confirmation_received=? WHERE id=?', 
        (1, id)
    )
    db.commit()

    return redirect(url_for('blog.index'))






