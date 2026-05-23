from flask import Flask
from app.routes.notification import notification_blueprint

app = Flask(__name__)

app.register_blueprint(notification_blueprint)