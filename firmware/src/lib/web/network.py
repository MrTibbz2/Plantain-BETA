import network
import time


class NetworkManager:
    def __init__(self):
        self.wlan = network.WLAN(network.STA_IF)
        self.ssid = None
        self.ip_addr = None

    def connect(self, ssid, password):
        self.wlan.active(True)
        if not self.wlan.isconnected():
            print(f'Connecting to {ssid}...')
            self.wlan.connect(ssid, password)
            for _ in range(20):
                if self.wlan.isconnected():
                    break
                time.sleep_ms(500)

        if self.wlan.isconnected():
            self.ssid = ssid
            self.ip_addr = self.wlan.ifconfig()[0]
            print(f'Connected! IP: {self.ip_addr}')
            return True

        print('Failed to connect')
        return False

    def disconnect(self):
        self.wlan.active(False)
        self.ssid = None
        self.ip_addr = None

    def get_status(self):
        return {
            'connected': self.wlan.isconnected(),
            'ssid': self.ssid,
            'ip': self.ip_addr
        }
