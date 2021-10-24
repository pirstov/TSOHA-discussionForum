from flask import Flask, session
from os import getenv

app = Flask(__name__)
app.config["SECRET_KEY"] = getenv("SECRET_KEY")

import routes
