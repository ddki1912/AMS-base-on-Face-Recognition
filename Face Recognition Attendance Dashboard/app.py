from flask import Flask
from datetime import timedelta
from controller.controller import Ctr
from flask_socketio import SocketIO
import numpy as np
import urllib

app = Flask(__name__)
app.config["SECRET_KEY"] = "iot19"
app.permanent_session_lifetime = timedelta(minutes=60)
app.register_blueprint(Ctr)
        
if __name__ == "__main__":
    app.run(port=8080, debug=True)
