# from flask import Flask

# def create_app():
#     app = Flask(__name__)
    
#     app.config['SECRET_KEY'] = "temporary-development-key"
    
#     from app.routes import main
    
#     app.register_blueprint(main)
    
#     return app


import os 
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY",
        "temporary-development-key"
    )
    
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///eam_monitoring.db"
    )
    
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    db.init_app(app)
    
    from app.routes import main
    app.register_blueprint(main)
    
    return app
        