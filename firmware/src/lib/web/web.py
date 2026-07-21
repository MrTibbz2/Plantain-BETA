from .microdot import Microdot
import json
from..debug.debug import DPrint

class Web:
    def __init__(self):
        self.__app = Microdot()
        self.__app_instance = None
        self._setup_routes()

    def set_app(self, app):
        """Set the app instance after Web is created."""
        self.__app_instance = app

    def _setup_routes(self):
        self.__app.route('/api/status')(self.get_status)
        self.__app.route('/api/configs')(self.get_configs)
        self.__app.route('/api/select/<name>', methods=['POST'])(self.select_config)
        self.__app.route('/api/config/<name>')(self.get_config)
        self.__app.route('/api/config', methods=['POST'])(self.save_config)
        self.__app.route('/api/config/<name>', methods=['DELETE'])(self.delete_config)
        self.__app.route('/<path:path>')(self.serve_static)
        self.__app.route('/')(self.serve_index)

    async def get_status(self, request):
        if not self.__app_instance:
            return json.dumps({'error': 'app not initialized'}), 500, {'Content-Type': 'application/json'}
        
        wifi_status = self.__app_instance.get_wifi_status()
        ble_status = self.__app_instance.get_ble_status()
        temp = self.__app_instance.get_temperature()
        
        return json.dumps({
            'wifi': {
                'connected': wifi_status['connected'],
                'ssid': wifi_status['ssid']
            },
            'bluetooth': {
                'connected': ble_status['connected'],
                'advertising': ble_status['advertising']
            },
            'temperature': temp
        }), 200, {'Content-Type': 'application/json'}

    async def get_configs(self, request):
        if not self.__app_instance:
            return json.dumps({'error': 'app not initialized'}), 500, {'Content-Type': 'application/json'}
        
        try:
            configs = self.__app_instance.get_configs()
            return json.dumps(configs), 200, {'Content-Type': 'application/json'}
        except Exception as e:
            return json.dumps({'error': str(e)}), 500, {'Content-Type': 'application/json'}

    async def select_config(self, request, name):
        """Set the active mapping to the named config. Returns ok or fail."""
        if not self.__app_instance:
            return json.dumps({'error': 'app not initialized'}), 500, {'Content-Type': 'application/json'}
        
        ok = self.__app_instance.select_config(name)
        status = 200 if ok else 404
        return json.dumps({'ok': ok}), status, {'Content-Type': 'application/json'}

    async def get_config(self, request, name):
        """Return the stored mappings for a named config without activating it."""
        if not self.__app_instance:
            return json.dumps({'error': 'app not initialized'}), 500, {'Content-Type': 'application/json'}
        
        data = self.__app_instance.get_config(name)
        if data is None:
            return json.dumps({'error': 'not found'}), 404, {'Content-Type': 'application/json'}
        return json.dumps(data), 200, {'Content-Type': 'application/json'}

    async def save_config(self, request):
        if not self.__app_instance:
            return json.dumps({'error': 'app not initialized'}), 500, {'Content-Type': 'application/json'}
        
        try:
            body = request.json
            filename = body.get('filename')
            mappings = body.get('mappings')
            if not filename or mappings is None:
                return json.dumps({'error': 'filename and mappings required'}), 400, {'Content-Type': 'application/json'}
            ok = self.__app_instance.save_config(filename, mappings)
            status = 200 if ok else 500
            return json.dumps({'ok': ok}), status, {'Content-Type': 'application/json'}
        except Exception as e:
            return json.dumps({'error': str(e)}), 500, {'Content-Type': 'application/json'}

    async def delete_config(self, request, name):
        if not self.__app_instance:
            return json.dumps({'error': 'app not initialized'}), 500, {'Content-Type': 'application/json'}
        
        ok = self.__app_instance.delete_config(name)
        status = 200 if ok else 404
        return json.dumps({'ok': ok}), status, {'Content-Type': 'application/json'}

    async def serve_index(self, request):
        try:
            with open('/lib/web/static/index.html', 'r') as f:
                return f.read(), 200, {'Content-Type': 'text/html'}
        except:
            return 'Not found', 404, {'Content-Type': 'text/plain'}

    async def serve_static(self, request, path):
        try:
            filepath = f'/lib/web/static/{path}'
            with open(filepath, 'r') as f:
                content = f.read()
            
            if path.endswith('.js'):
                content_type = 'application/javascript'
            elif path.endswith('.css'):
                content_type = 'text/css'
            elif path.endswith('.html'):
                content_type = 'text/html'
            else:
                content_type = 'text/plain'
            
            return content, 200, {'Content-Type': content_type}
        except:
            return 'Not found', 404, {'Content-Type': 'text/plain'}

    async def run(self):
        DPrint("WEB: running server on port 80")
        await self.__app.start_server(port=80)
