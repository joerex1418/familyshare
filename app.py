import sqlite3
import pathlib

import rich
from flask import request, json
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
    return {"print": print, "type": type, "str": str, "int": int}

@app.route("/")
def index():
    return render_template('index.html', PAGE_TITLE="Index")

@app.route("/attic", methods=["GET", "POST"])
def attic():
    attic_data = api.get_attic_data()
    if request.method == "GET":
        return render_template("pages/attic.html", PAGE_TITLE="Attic", attic_data=attic_data)
    
    # New Attic Post
    if request.method == "POST":
        print("Form Data")
        rich.print(request.form, end="\n")
        # print("Photo")
        # rich.print(type(request.form["photo"]), end="\n")
        print("Files")
        rich.print(request.files, end="\n")
        
        return render_template("pages/attic.html", PAGE_TITLE="Attic", attic_data=attic_data)

if __name__ == "__main__":
    app.run("127.0.0.1",port=5500,debug=True)
