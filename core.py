
import json
import codecs
import argparse
import time
import datetime
import shutil
import os
import re
import math
import yaml
import numpy
import string
import subprocess
import asyncio
import sys
import importlib
import threading
from db import DB
from ws import WS

colors = {
    "BLACK": "\033[30m",
    "RED": "\033[31m",
    "GREEN": "\033[32m",
    "YELLOW": "\033[33m",
    "BLUE": "\033[34m",
    "MAGENTA": "\033[35m",
    "CYAN": "\033[36m",
    "WHITE": "\033[37m",
    "UNDERLINE": "\033[4m",
    "RESET": "\033[0m"
}

class CoreObject:
    _working_dir = None;

    def __init__(self):
        self.ws = WS()
        self.db = DB()
        self.log( "inited" )

    def log ( self, text, color="CYAN" ):  
        c = colors[color]
        now = datetime.datetime.now()
        f_data = now.strftime("%H:%M:%S")
        print( f"{c}[{f_data}] TWORKER ({self.__class__.__name__}): {text}" )

        if ( self.ws.server_started ):
            try:
                self.ws.broadcast( {
                    "event": "log",
                    "data": {
                        "source": self.__class__.__name__,
                        "text": text,
                        "thread_id": threading.get_ident(),
                        "text_color": color
                    }
                } )
            except Exception as e:
                self.log(f"error while sending logs over websockets {str(e)}", e)

        return self

    @property
    def working_dir( self ):
        return CoreObject._working_dir

    def set_working_dir ( self, working_dir ):
        if ( CoreObject._working_dir != None ):
            self.log("working directory is already set", "YELLOW")
            return None
        else:
            sys.path.append(working_dir)
            CoreObject._working_dir = working_dir

    def get_args( self, params  ):
        parser = argparse.ArgumentParser()

        for p in params:
            parser.add_argument( f"--{p['name']}", help=p["help"])
        
        try:
            return parser.parse_args()
        except Exception as e:
            self.log(f"error when parsing arguments: { str(e) }", "RED")
            return None

    def join_path ( self, *args ):
        try:
            return os.path.join( *args ).replace( os.sep, "/" )
        except Exception as e:
            self.log(f"error while joining path {str(e)}", "RED")
            print(*args)
            return None


    def exit_app( self, before_exit_message ):
        self.log( before_exit_message, "RED" )
        self.log("exiting app...", "RED")
        sys.exit()

    def read_json( self, p ):
        try:
            file = codecs.open(p, "r", "utf_8_sig")
            data_string = file.read()
            file.close()
            data = json.loads( data_string )
            return data
        except Exception as e:
            self.log(f"error while reading { p }: { str(e) }", "RED")
            return None

    def string_of_char ( self, character, target_len=0 ):
        r = ""
        while len(r) < target_len: 
            r += character
        return r

    def log_dict ( self, data, color="GREEN" ):
        try:self.log( json.dumps( data, indent=4 ), color )
        except Exception as e: self.log( f"error while printing dict: { str(e) }" )
        return self

    def import_script ( self, path ):
        module = None
        try:
            module = importlib.__import__( path )
            self.log(f"script found at working TWorker`s library: { path }", "GREEN" )
            return module
        except Exception as e:
            self.log(f"error while importing script from TWorker`s library: { path }, { str(e) }", "RED" )

        if ( module == None ):
            self.log(f"error while loading module { path }", "RED").log("module not found", "RED")

        return module

    def sleep ( self, d ):
        self.log(f"sleeping for {d}s")
        time.sleep(d)

    def run_while_loop ( self, duration=-1 ):
        if duration < 0:
            while (True):
                ""