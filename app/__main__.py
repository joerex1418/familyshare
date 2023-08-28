import uuid
import sqlite3
import pathlib
import importlib
import importlib.util

import rich
from flask import request
from flask.app import Flask
from flask.json import jsonify
from flask.helpers import url_for
from flask.helpers import redirect
from flask.helpers import send_from_directory
from flask.templating import render_template
from flask_assets import Environment, Bundle
from werkzeug.utils import secure_filename
from werkzeug.datastructures.file_storage import FileStorage

from src import api

UPLOAD_FOLDER = "static"
ALLOWED_EXTENSIONS = ['pdf', 'png', 'jpg', 'jpeg', 'gif']

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DATABASE'] = 'data.db'
app.config['SECRET_KEY'] = 'ArrakisRunsOnDuncan!!LetoIIForPrez'

# rich.print(dict(app.config).keys())

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
        
        item_id = str(uuid.uuid4())
        api.add_to_attic(
            item_id,
            title=request.form["title"],
            posted_by="N/A",
            media_content=[fp for fp in request.files.values()],
            description=request.form["description"],
            belongs_to=request.form["belongs-to"],
            discovery_location=request.form["found-in"],
            last_chance_datetime=request.form["last-chance-date"]
        )
        
        return render_template("pages/attic.html", PAGE_TITLE="Attic", attic_data=attic_data)

if __name__ == "__main__":
    app.run("127.0.0.1",port=5500,debug=True)
