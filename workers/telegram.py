from worker import Worker  

class Telegram(Worker):

    def load( self, worker_config ):
        self.log(f"loading...")
