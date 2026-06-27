import asyncio
import aioble # type: ignore | only available on mp.
import bluetooth # type: ignore
from .uuids import MIDI_SERVICE_UUID, MIDI_CHAR_UUID
import json 
import io # type: ignore
class ble: # class for setting up and using bluetooth midi. 
    def __init__(self):
        self.MIDI_SERVICE_UUID = MIDI_SERVICE_UUID
        self.MIDI_CHAR_UUID = MIDI_CHAR_UUID
        self.__ble_service = aioble.Service(self.MIDI_SERVICE_UUID)
        self.__device_name = "Plantain-MIDI"
        self.__connection = None
        self.__midi_char = aioble.Characteristic(
            self.__ble_service,
            MIDI_CHAR_UUID,
            read=True,
            write=True,
            notify=True,
            write_no_response=True,
        )
        aioble.register_services(self.__ble_service)   
    
    def set_device_name(self, name: str):
        self.__device_name = str(name)
    
    
    async def run(self):
        while True:
            async with await aioble.advertise(
                100_000,
                name=self.__device_name,
                services=[self.MIDI_SERVICE_UUID],
            ) as connection:
                self.__connection = connection
                print(f"connected to device.")
                while connection.is_connected():
                    try:
                        pass
                        # tx = bytearray([0x80, 0x80, 0x90, 0x3C, 0x64])
                        # self.__midi_char.notify(self.__connection, tx)
                    except:
                        pass
                    await asyncio.sleep_ms(100)
                self.__connection = None
                print(f"device disconnected.")


    def __transmit(self, data: bytes):
        if self.__connection and self.__connection.is_connected():
            self.__midi_char.notify(self.__connection, data)

class MIDI: 
    def __init__(self, ble: ble):
        self.__ble = ble
        self.__button_index = ButtonIndex()
    
class ButtonIndex:
    def __init__(self):
        self.__button_to_note_index = []

    def load_config(self, config_path: str):
        pass