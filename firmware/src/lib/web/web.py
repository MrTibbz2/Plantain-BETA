from microdot import Microdot 
import json
from .. import pl_bluetooth
# required routes/apis:

# getconfigs: list of config file names

# load config: gets a config by filename: returns a mapping json object

# save config: mappings, filename. saves the object as a config\

# deleteconfig: filename

# getstatus: {wifi: {connected, ssid}, bluetooth: {connected, advertising}, temp}




    
class Web: 
# class for handling handlers that handle the handling of handlers to handle the web requests.
    def __init__(self, buttonIndex): 
        self.__app = Microdot()
        self.__buttonIndex = buttonIndex
    

    def _setup_routes(self):
        self.__app.route('/api/status')(self.get_status)
        self.__app.route('/api/configs')(self.get_configs)
        self.__app.route('/api/select/<name>')(self.select_config)

    async def get_status(self, request):
        pass

    async def get_configs(self, request):
        pass
    async def select_config(self, request):
        pass



    

    

