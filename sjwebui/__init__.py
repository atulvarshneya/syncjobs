from flask import Flask
from flaskconfig import flaskconfig

app = Flask(__name__)
app.config.from_object(flaskconfig)

from sjwebui import routes
