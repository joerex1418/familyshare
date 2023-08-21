import os
import uuid
import typing
import shutil
import pathlib
import sqlite3
import datetime as dt

PathLike = typing.Union[os.PathLike, pathlib.Path]
DATETIME_FMT = r"%Y-%m-%d_%H:%M:%S"

from .paths import VAULT_DIR

def dict_factory(cursor, row):
    colnames = [c[0] for c in cursor.description]
    return {k:v for k,v in zip(colnames, row)}

def get_db_connection():
    _path = VAULT_DIR.joinpath("data.db")
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
                id TEXT,
                title TEXT,
                image_name TEXT,
                description TEXT,
                belongs_to TEXT,
                discovery_location TEXT,
                last_chance_datetime TEXT,
                created_at_datetime TEXT
            )
            """
        )
        
        conn.commit()

def add_to_attic(title:str, image_name:typing.Union[pathlib.Path,str]=None, description:str=None, belongs_to:str=None, discovery_location:str=None, last_chance_datetime:str=None):
    with get_db_connection() as conn:
        c = conn.cursor()
        
        item_id = str(uuid.uuid4())
        
        if isinstance(last_chance_datetime, (dt.date, dt.datetime)):
            last_chance_datetime = last_chance_datetime.strftime(DATETIME_FMT)
        
        new_post_data = {
            "id": item_id,
            "title": title,
            "image_name": image_name,
            "description": description,
            "belongs_to": belongs_to,
            "discovery_location": discovery_location,
            "last_chance_datetime": last_chance_datetime,
            "created_at_datetime": dt.datetime.today().strftime(DATETIME_FMT)
        }
        placeholder_keys = [f":{k}" for k in new_post_data.keys()]
        placeholder_keys_string = ",".join(placeholder_keys)
        
        c.execute(
            f"""
            INSERT INTO attic 
            (id, title, image_name, description, belongs_to, discovery_location, last_chance_datetime, created_at_datetime) 
            
            VALUES ({placeholder_keys_string})
            """,
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
        
        return data