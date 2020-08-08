
import sqlite3
import os
import json


class DB:
    connection = None
    databases = {}
    working_dir_path = None
    workind_database = None

    def __init__(self):
        ""

    

    def set_json ( self, alias, data ):
        string = json.dumps( data )

        self.replace( {
            "table_name": "json",
            "data": {
                "object": string
            },
            "condition": f"alias='{alias}'"
        } )

        # self.insert( {
        #     "table_name": "json",
        #     "data": {
        #         "alias": alias,
        #         "object": string
        #     }
        # } )

    def get_json ( self, alias ):
        data = self.select_from( {
            "table_name": "json",
            "prop_name": "alias",
            "prop_value": alias
        } )

        if ( data != None ):
            string = data[1]
            try: return json.loads( string )
            except Exception as e: print(f"db: error while reading json: {str(e)}")
        else:
            return None
        

    def get_all ( self, params ):
        try:
            conn = self.get_connection()
            c = conn.cursor()
            c.execute(params["query"])
            conn.commit()
            return c.fetchall()
        except Exception as e:
            print("\033[91mdb ERROR!", params["query"],  str(e))
            return e

    def get ( self, params ):
        try:
            conn = self.get_connection()
            c = conn.cursor()
            c.execute(params["query"])
            conn.commit()
            return c.fetchone()
        except Exception as e:
            print("\033[91mdb ERROR!", params["query"],  str(e))
            return e

    def update( self, params ):
        q = f"UPDATE { params['table_name'] } "
        q+= f"SET { self.serialize_set_params( params['data'] ) }"
        q+= f"WHERE { params['condition'] };"

        return self.get( {
            "query": q
        } )

    def replace( self, params ):
        q = f"REPLACE INTO { params['table_name'] } "
        q+= f"SET { self.serialize_set_params( params['data'] ) }"
        q+= f"WHERE { params['condition'] };"

        return self.get( {
            "query": q
        } )

    def select_from ( self, params ):
        q = f"SELECT * FROM { params['table_name'] } WHERE { params['prop_name'] }='{ params['prop_value'] }'"
        # print(self.workind_database, q)
        return self.get( {
            "query": q
        } )

    def select_all_from ( self, params ):
        q = f"SELECT * FROM { params['table_name'] } WHERE { params['prop_name'] }='{ params['prop_value'] }'"
        # print(self.workind_database, q)
        return self.get_all( {
            "query": q
        } )

    def stringify( self, data ):
        if ( data == None ):
            return "'null'"
        if  isinstance(data, str): 
            data = data.replace("'", "`")
        if  isinstance(data, bool): 
            if data:
                return "'true'"
            else:
                return "'false'"

        return f"'{data}'"

    def serialize_set_params ( self, data ):
        r = []
        for k in data.keys():
            d = data[k]
            r.append(f"{k} = '{d}'")

        return ", ".join(r)

    def insert ( self, params ):
        q = f"INSERT INTO { params['table_name'] } ({ ', '.join( params['data'].keys() ) }) VALUES "
        q += f"({', '.join( map(lambda i:  self.stringify(i), params['data'].values() ) )});"

        return self.get( {
            "query": q
        } )

    def insert_few ( self, params ):
        q = None

        for item in params["data"]:
            if q == None:
                q = f"INSERT INTO { params['table_name'] } ({ ', '.join( item.keys() ) }) VALUES"
            q = q + f"\n({', '.join( map(lambda i:  self.stringify(i), item.values() ) )}),"

        # print(q)

        q = q[0:len(q)-1]

        return self.get( {
            "query": q
        } )

    def insert_or_update ( self, params ):
        q = f"REPLACE INTO { params['table_name'] }( { ', '.join( params['data'].keys() ) } ) VALUES({ ', '.join( map(lambda i:  self.stringify(i), params['data'].values()) ) });"
        print("db", self.workind_database, q)
        return self.get( {
            "query": q
        } )

    def create_table ( self, params ):
        q = f"CREATE TABLE { params['table_name'] } ({( ', '.join(params['cols'].keys()) )});"
        print("db", self.workind_database, q)
        return self.get( {
            "query": q
        } )

    def get_connection ( self ):
        if ( DB.connection ):
            return DB.connection
        else:
            conn = sqlite3.connect( os.path.join( self.working_dir_path, self.workind_database ), timeout=90 )
            DB.connection = conn
            return conn

    def set_working_dir ( self, dir_path ):
        if ( DB.working_dir_path != None ):
            print(f"db: working directory is already set")
            return None
        
        DB.working_dir_path = dir_path
        if ( DB.workind_database ): self.init_db()

    def set_working_db ( self, db_name ):
        if ( DB.workind_database != None ):
            print(f"db: working database is already set")
            return None
        
        DB.workind_database = db_name
        if ( DB.working_dir_path ): self.init_db()

    def init_db( self ):
        db = self.get_connection()
        self.create_table( {
            "table_name": "json",
            "cols": {
                "alias": "TEXT",
                "object": "TEXT"
            }
        } )
        print(db)
    
