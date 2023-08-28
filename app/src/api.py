import os
import uuid
import typing
import shutil
import pathlib
import sqlite3
import datetime as dt

from werkzeug.utils import secure_filename
from werkzeug.datastructures.file_storage import FileStorage

PathLike = typing.Union[os.PathLike, pathlib.Path]
DATETIME_FMT = r"%Y-%m-%d_%H:%M:%S"

from .paths import ROOT_DIR

STATIC = ROOT_DIR.joinpath("static")
STATIC_IMAGES = STATIC.joinpath("images")

def dict_factory(cursor, row):
    colnames = [c[0] for c in cursor.description]
    return {k:v for k,v in zip(colnames, row)}

def get_db_connection():
    _path = ROOT_DIR.joinpath("data.db")
    conn = sqlite3.connect(_path)
    conn.row_factory = dict_factory
    return conn

def upload_file(_srcfile: PathLike, _dest: PathLike = None, /):
    if isinstance(_srcfile,str):
        _srcfile = pathlib.Path(_srcfile)
    
    if _dest.is_dir():
        _dest = _dest.joinpath(str(_srcfile.name))
    
    shutil.copyfile(_srcfile, _dest)
    
def create_attic_table():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.executescript(
            """
            DROP TABLE IF EXISTS attic;
            
            CREATE TABLE attic (
                item_id TEXT,
                title TEXT,
                posted_by TEXT,
                image_count INTEGER,
                content_path TEXT,
                description TEXT,
                belongs_to TEXT,
                discovery_location TEXT,
                last_chance_datetime TEXT,
                created_at_datetime TEXT
            )
            """
        )
        
        conn.commit()

def add_to_attic(
    item_id:typing.Union[str,uuid.uuid4],/,
    title:str,
    posted_by:str,
    media_content:typing.List[FileStorage]=None,
    description:str=None,
    belongs_to:str=None,
    discovery_location:str=None,
    last_chance_datetime:str=None
    ):
    with get_db_connection() as conn:
        c = conn.cursor()
        
        if isinstance(last_chance_datetime, (dt.date, dt.datetime)):
            last_chance_datetime = last_chance_datetime.strftime(DATETIME_FMT)
        elif isinstance(last_chance_datetime, str):
            last_chance_date = dt.datetime.strptime(last_chance_datetime, r"%Y-%m-%d")
            last_chance_datetime = dt.datetime.combine(last_chance_date, dt.time(0,0,0))
        
        last_chance_datetime: dt.datetime
        
        image_count = len(media_content)
        content_path = STATIC_IMAGES.joinpath("attic", f"{item_id}")
        if not content_path.exists() and image_count != 0:
            content_path.mkdir()
        
        for file_object in media_content:
            file_object.save(content_path.joinpath(secure_filename(file_object.filename)))
        
        new_post_data = {
            "item_id": item_id,
            "title": title,
            "posted_by": posted_by,
            "image_count": image_count,
            "content_path": str(content_path),
            "description": description,
            "belongs_to": belongs_to,
            "discovery_location": discovery_location,
            "last_chance_datetime": last_chance_datetime.strftime(DATETIME_FMT),
            "created_at_datetime": dt.datetime.today().strftime(DATETIME_FMT)
        }
        
        placeholder_keys = [f":{k}" for k in new_post_data.keys()]
        placeholder_keys_string = ",".join(placeholder_keys)
        keys_string = placeholder_keys_string.replace(":","")
        
        c.execute(
            f"INSERT INTO attic ({keys_string}) VALUES ({placeholder_keys_string})",
            new_post_data
        )
        
        conn.commit()

def get_attic_data() -> typing.List[typing.Dict]:
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM attic")
        data = c.fetchall()
        
        for d in data:
            d["created_at_datetime"] = dt.datetime.strptime(d["created_at_datetime"], DATETIME_FMT)
            d["last_chance_datetime"] = dt.datetime.strptime(d["last_chance_datetime"], DATETIME_FMT)
            d["content_directory_name"] = pathlib.Path(d["content_path"]).name
            d["content_filenames"] = [x.name for x in pathlib.Path(d["content_path"]).glob('**/*') if x.is_file()]
            # images_string_list = d["images_list"].split("|=|")
            # if images_string_list == ['']:
            #     images_string_list = []
            # d["images_list"] = images_string_list
        
        return data
