import sqlite3
import pathlib

from flask import request
from flask.app import Flask
from flask.json import jsonify
from flask.templating import render_template
from flask.helpers import url_for
from flask_assets import Environment, Bundle

from src import api

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False
app.config['UPLOAD_FOLDER'] = 'VAULT'
app.config['DATABASE'] = 'data.db'

assets = Environment(app)
scss = Bundle('style.scss',filters='pyscss',output='style.css')
assets.register('style',scss)

@app.context_processor
def inject_dict_for_all_templates():
    return {"print": print}

@app.route("/")
def index():
    return render_template('index.html', PAGE_TITLE="Index")

@app.route("/attic")
def attic():
    attic_data = api.get_attic_data()
    return render_template("pages/attic.html", 
                           PAGE_TITLE="Attic",
                           attic_data=attic_data)

if __name__ == "__main__":
    app.run("127.0.0.1",port=5500,debug=True)
