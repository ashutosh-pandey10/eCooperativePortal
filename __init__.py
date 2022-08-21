import os
from flask import (
    Flask, flash, request, redirect, url_for, render_template
)
from werkzeug.utils import secure_filename

def create_app(test_config=None):
    #creating and configuring app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)

    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    absolute_path = os.path.abspath(os.path.dirname(__file__))
    parent_dir = os.path.join(absolute_path, os.pardir) 
    app.config['UPLOAD_FOLDER'] = os.path.join(parent_dir, 'uploaded_files')

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import admin
    app.register_blueprint(admin.bp)

    from . import inventory
    app.register_blueprint(inventory.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app        