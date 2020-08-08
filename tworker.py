from core import CoreObject  
import sys
import threading
import random
import asyncio
import time

sys.path.append( "workers" )

class TWorker( CoreObject ):
    def __init__( self ):
        super().__init__() 
        self.log("inited", "GREEN")
        args = self.get_args([
            { "name": "dir", "help": "path working directory" }
        ])
        

        if args.dir == None:
            self.exit_app( "please provide path to working directory with tworker.config.json file using --dir option" ) 
        else:
            self.set_working_dir( args.dir )
            self.init_tworker( args.dir )

    def init_tworker( self, dir_path ):
        config = self.read_json( self.join_path( dir_path, "tworker.config.json" ) )
        if config == None: self.exit_app( "tworker.config.json file not found" )
        self.config = config
        self.log("\nCONFIG FILE:", "GREEN").log_dict(config)

        if "WEBSOCKETS" in config:
            self.setup_ws( config["WEBSOCKETS"] )

        self.sleep(2)

        db_name = config["DB_NAME"] if "DB_NAME" in config else "tworker.db"
        self.log(f"working database: { dir_path }/{ db_name }", "MAGENTA")
        self.db.set_working_dir( dir_path )
        self.db.set_working_db( db_name )
        
        # self.db.set_json( "kek", {
        #     "AAAA": 1,
        #     "bdbdBBBfbdfg": False
        # } )
        
        if ( "WORKERS" in config ): 
            self.init_workers( config["WORKERS"] )
        else: 
            self.exit_app( "please provide data for at least one worker" )

        t1 = threading.Thread(target=self.test_daemon, args=( "Some Thread", "0.75", "RED" ))
        t1.daemon = True
        t1.start()

        t2 = threading.Thread(target=self.test_daemon, args=( "Yet Another Thread", "1", "CYAN" ))
        t2.daemon = True
        t2.start()

        t3 = threading.Thread(target=self.test_daemon, args=( "And Event Yet Another One", "1.5", "MAGENTA" ))
        t3.daemon = True
        t3.start()

        # self.run_while_loop()
        while True:
            self.log("kekekeke")
            self.log("Привет, бандиты", "RED")
            self.log("Ну, здаров", "MAGENTA")
            self.ws.emit("log", {
                "source": "Random",
                "text": str(random.random()),
                "text_color": "GREEN"
            })
            self.sleep(random.random() * 5)

    def test_daemon ( self, name, delay, color ):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        while True:
            self.ws.emit("log", {
                "source": name,
                "text": self.randomword(32),
                "text_color": color
            })

            time.sleep(float(delay))

    def init_workers ( self, workers_config ):
        self.log(f"start initalising workers {len( workers_config )}")
        for w in workers_config:
            self.init_worker( w )
    
    def init_worker ( self, worker_config ):
        self.log("initializing worker", "MAGENTA")
        if ( "SCRIPT" in worker_config ):
            script_path = worker_config["SCRIPT"]
            script = self.import_script( script_path )
            print(script)
            print(script)
            self.log_dict( worker_config, "RED" )
        else:
            self.log("error while creating worker: no SCRIPT field provided", "RED").log_dict( worker_config, "RED" )

    def setup_ws( self, ws_config ):
        self.log("initialising websockets...", "YELLOW" ).log_dict( ws_config, "YELLOW" )
        self.ws.start( ws_config["HOST"], ws_config["PORT"] )


tworker = TWorker()