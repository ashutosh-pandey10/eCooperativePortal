import os
import functools

from flask import (
    Blueprint, flash, current_app, g, redirect, render_template, session, request, url_for, send_from_directory
)

from flaskr.db import get_db
from flaskr.auth import login_required
from flaskr.admin import admin_login_required


bp = Blueprint('inventory', __name__, url_prefix='/inventory')

@bp.route('/view', methods = ('POST', 'GET'))
def view():
    db = get_db()
    items = db.execute(
        'SELECT * FROM inventory'
    ).fetchall()
    return render_template('blog/inventory.html', items=items)


@bp.route('/add_item', methods = ('POST', 'GET'))
@admin_login_required
def add_item():
    if request.method == 'POST':
        itemname = request.form['itemname']
        itemcost = request.form['itemcost']
        itemquant = request.form['itemquant']

        db = get_db()
        error = None

        if not itemname:
            error = "Item name is required!"
        elif not itemcost:
            error = "Item cost is required!"
        elif not itemquant:
            error = "Quantity of Item available must be mentioned!"

        elif db.execute(
            'SELECT id FROM inventory WHERE item_name = ?', (itemname,)
        ).fetchone() is not None:
            error = "Item {} already exists. Try updating the same!".format(itemname)        
        
        if error is None:
            db.execute(
                'INSERT INTO inventory (item_name, item_cost, item_quantity) VALUES (?, ?, ?)',
                (itemname, itemcost, itemquant)
            )
            db.commit()
            return redirect(url_for('inventory.view'))
    
        flash(error)
    return render_template('blog/add_item.html')


@bp.route('/<itemname>/update_item', methods=('POST', 'GET'))
@admin_login_required
def update_item(itemname):
    if request.method == 'POST':
        itemquantity = request.form['itemquantity']
        itemcost = request.form['itemcost']
        db = get_db()
        error = None

        itemquantity = int(itemquantity)
        itemcost = int(itemcost)

        if itemcost < 0:
            error = "Invalid Input!"
        elif itemquantity < 0:
            error = "Invalid Input!"
        else:
            db.execute(
                'UPDATE inventory SET item_quantity = ?, item_cost = ? WHERE item_name = ?',
                (itemquantity, itemcost, itemname,)
            )        
            db.commit()
            return redirect(url_for('inventory.view'))
        
        flash(error)
    return render_template('blog/update_inventory.html', itemname=itemname)


@bp.route('/<itemname>/delete_item', methods=('POST', 'GET'))
@admin_login_required
def delete_item(itemname):
    db = get_db()
    db.execute(
        'DELETE FROM inventory WHERE item_name = ?',(itemname,)
    )    
    db.commit()
    
    return redirect(url_for('inventory.view'))


@bp.route('/<itemname>/<itemcost>/<itemquantity>/item_order', methods = ['POST', 'GET'])
@login_required
def item_order(itemname, itemcost, itemquantity):
    if request.method == 'POST':
        item_quant = request.form['item_quant']
        db = get_db()
        error = None
        item_quant = int(item_quant)

        # print(itemname,itemcost, itemquantity)
        
        try:
            if error is None:
                total_cost = item_quant*int(itemcost)
                db.execute(
                    'INSERT INTO itemorder (order_id, item_name, order_cost, item_quantity) VALUES(?, ?, ?, ?)',
                    (g.user['id'], itemname, total_cost, item_quant,)
                )
                db.commit()
                updated_quant = int(itemquantity) - item_quant
                db.execute(
                    'UPDATE inventory SET item_quantity = ? WHERE item_name = ?',
                    (updated_quant, itemname,)
                )
                db.commit()

                return redirect(url_for('blog.index'))
        except Exception as e: 
            raise(e)        
        
        flash(error)
    return render_template('blog/checkout.html', itemname=itemname, itemcost=itemcost, itemquantity=itemquantity)

