import logging

from flask import Flask
from app.routes.notification import notification_blueprint

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

app = Flask(__name__)

app.register_blueprint(notification_blueprint)