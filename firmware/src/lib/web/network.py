import network
import machine # type: ignore


class NetworkManager:
    def __init__(self):
        self.wlan = None
        self.connected = False
        self.ssid = None
        self.ip_addr = None

    def connect(self, ssid, password):
        """Connect to WiFi network."""
        try:
            self.wlan = network.WLAN(network.STA_IF)
            self.wlan.active(True)
            
            if not self.wlan.isconnected():
                print(f'Connecting to {ssid}...')
                self.wlan.connect(ssid, password)
                
                timeout = 0
                while not self.wlan.isconnected() and timeout < 20:
                    machine.idle()
                    timeout += 1
            
            if self.wlan.isconnected():
                self.connected = True
                self.ssid = ssid
                self.ip_addr = self.wlan.ifconfig()[0]
                print(f'Connected! IP: {self.ip_addr}')
                return True
            else:
                print('Failed to connect')
                return False
        except Exception as e:
            print(f'Connection error: {e}')
            return False

    def disconnect(self):
        """Disconnect from WiFi."""
        try:
            if self.wlan:
                self.wlan.active(False)
            self.connected = False
            self.ssid = None
            self.ip_addr = None
            return True
        except Exception as e:
            print(f'Disconnect error: {e}')
            return False

    def is_connected(self):
        """Check if connected to WiFi."""
        try:
            if self.wlan:
                return self.wlan.isconnected()
            return False
        except:
            return False

    def get_status(self):
        """Get WiFi status."""
        return {
            'connected': self.is_connected(),
            'ssid': self.ssid,
            'ip': self.ip_addr
        }
