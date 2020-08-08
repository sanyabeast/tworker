from core import CoreObject 

class Worker(CoreObject):
    def __init__( self, config ):
        super().__init__()
        self.load( config )

    def load( self, config ):
        self.log( "initialize...", config )
        self.log(f"working directory is: {self.working_dir}")