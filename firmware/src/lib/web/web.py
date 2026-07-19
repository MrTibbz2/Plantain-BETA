from microdot import Microdot
import json


class Web:
    def __init__(self, buttonIndex):
        self.__app = Microdot()
        self.__buttonIndex = buttonIndex
        self._setup_routes()

    def _setup_routes(self):
        self.__app.route('/api/status')(self.get_status)
        self.__app.route('/api/configs')(self.get_configs)
        self.__app.route('/api/select/<name>', methods=['POST'])(self.select_config)
        self.__app.route('/api/config/<name>')(self.get_config)
        self.__app.route('/api/config', methods=['POST'])(self.save_config)
        self.__app.route('/api/config/<name>', methods=['DELETE'])(self.delete_config)

    async def get_status(self, request):
        return json.dumps({
            'wifi': {'connected': False, 'ssid': None},
            'bluetooth': {'connected': False, 'advertising': False},
            'temperature': None
        }), 200, {'Content-Type': 'application/json'}

    async def get_configs(self, request):
        try:
            configs = self.__buttonIndex.get_configs()
            return json.dumps(configs), 200, {'Content-Type': 'application/json'}
        except Exception as e:
            return json.dumps({'error': str(e)}), 500, {'Content-Type': 'application/json'}

    async def select_config(self, request, name):
        """Set the active mapping to the named config. Returns ok or fail."""
        ok = self.__buttonIndex.select_config(name)
        status = 200 if ok else 404
        return json.dumps({'ok': ok}), status, {'Content-Type': 'application/json'}

    async def get_config(self, request, name):
        """Return the stored mappings for a named config without activating it."""
        data = self.__buttonIndex.get_config(name)
        if data is None:
            return json.dumps({'error': 'not found'}), 404, {'Content-Type': 'application/json'}
        return json.dumps(data), 200, {'Content-Type': 'application/json'}

    async def save_config(self, request):
        try:
            body = request.json
            filename = body.get('filename')
            mappings = body.get('mappings')
            if not filename or mappings is None:
                return json.dumps({'error': 'filename and mappings required'}), 400, {'Content-Type': 'application/json'}
            ok = self.__buttonIndex.save_config(filename, mappings)
            status = 200 if ok else 500
            return json.dumps({'ok': ok}), status, {'Content-Type': 'application/json'}
        except Exception as e:
            return json.dumps({'error': str(e)}), 500, {'Content-Type': 'application/json'}

    async def delete_config(self, request, name):
        ok = self.__buttonIndex.delete_config(name)
        status = 200 if ok else 404
        return json.dumps({'ok': ok}), status, {'Content-Type': 'application/json'}

    async def run(self):
        await self.__app.start_server(port=80)
