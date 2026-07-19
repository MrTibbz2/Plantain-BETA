from lib.debug.debug import DPrint
import lib.pl_bluetooth.pl_bluetooth
import lib.switchbutton_sensor.switch_manager
from lib.web.network import NetworkManager
from collections import deque
import asyncio
import lib.web.web


class App:
    def __init__(self, wifi_ssid=None, wifi_password=None):
        self.__network = NetworkManager()
        self.__web = lib.web.web.Web()
        self.__web.set_app(self)
        self.__ble = lib.pl_bluetooth.pl_bluetooth.ble()
        self.__buttonIndex = lib.pl_bluetooth.pl_bluetooth.ButtonIndex()
        self.__midi = lib.pl_bluetooth.pl_bluetooth.MIDI(self.__ble, self.__buttonIndex)
        self.__switchMgr = lib.switchbutton_sensor.switch_manager.SwitchMgr(self.MIDIQ_append_cb)
        self.MIDIQueue = deque([], 8)
        self.ble_connected = False
        self.ble_advertising = False
        self.temperature = None
        
        if wifi_ssid and wifi_password:
            DPrint(f"Connecting to WiFi: {wifi_ssid}")
            self.__network.connect(wifi_ssid, wifi_password)
        else:
            DPrint("WiFi credentials not provided")

    def MIDIQ_append_cb(self, i):
        self.MIDIQueue.append(i)
        if len(self.MIDIQueue) > 7:
            DPrint("WARNING: MIDIQueue is overflowing. consider a different approach long term. (mate youre fucked)")

    def get_wifi_status(self):
        """Get WiFi status."""
        return self.__network.get_status()

    def get_ble_status(self):
        """Get BLE status."""
        return {
            'connected': self.ble_connected,
            'advertising': self.ble_advertising
        }

    def get_temperature(self):
        """Get device temperature."""
        return self.temperature

    def set_ble_connected(self, connected):
        """Update BLE connection status."""
        self.ble_connected = connected

    def set_ble_advertising(self, advertising):
        """Update BLE advertising status."""
        self.ble_advertising = advertising

    def set_temperature(self, temp):
        """Update device temperature."""
        self.temperature = temp

    def connect_wifi(self, ssid, password):
        """Connect to WiFi network."""
        return self.__network.connect(ssid, password)

    def disconnect_wifi(self):
        """Disconnect from WiFi."""
        return self.__network.disconnect()

    def get_configs(self):
        """Get list of configurations."""
        return self.__buttonIndex.get_configs()

    def select_config(self, name):
        """Select and activate a configuration."""
        return self.__buttonIndex.select_config(name)

    def get_config(self, name):
        """Get configuration data without activating."""
        return self.__buttonIndex.get_config(name)

    def save_config(self, filename, mappings):
        """Save a configuration."""
        return self.__buttonIndex.save_config(filename, mappings)

    def delete_config(self, name):
        """Delete a configuration."""
        return self.__buttonIndex.delete_config(name)

    async def run(self):
        await asyncio.gather(
            self.__ble.run(),
            self.__web.run(),
            self._main_loop()
        )

    async def _main_loop(self):
        while True:
            if self.MIDIQueue:
                item = self.MIDIQueue.popleft()
                if item[1] == True:
                    DPrint("APP: sending Note on msg. ")
                    self.__midi.note_on(item[0])
                else:
                    self.__midi.note_off(item[0])
                    DPrint("APP: sending Note off msg. ")

            await asyncio.sleep_ms(10)
