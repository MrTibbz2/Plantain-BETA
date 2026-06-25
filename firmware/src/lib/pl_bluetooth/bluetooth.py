import asyncio
import aioble # type: ignore | only available on mp.
import bluetooth
from uuids import MIDI_SERVICE_UUID, MIDI_CHAR_UUID


class ble: # class for setting up 
    def __init__(self):
        self.MIDI_SERVICE_UUID = MIDI_SERVICE_UUID
        self.MIDI_CHAR_UUID = MIDI_CHAR_UUID
        self.__ble_service = aioble.Service(self.MIDI_SERVICE_UUID)
        self.__device_name = ""

        self.__midi_char = aioble.Characteristic(
            self.__ble_service,
            MIDI_CHAR_UUID,
            write=True,
            notify=True,
            write_no_response=True,
        )
        aioble.register_services(self.__ble_service)   
    
    def set_device_name(name: str, self):
        self.__device_name = str(name)
    
    
    async def run(self):
        while True:
            
            async with await aioble.advertise(
                100_000,
                name=self.__device_name,
                services=[self.MIDI_SERVICE_UUID],
            ) as self.connection:

                print(f"connected to device.")

                while self.connection.is_connected():
                    await asyncio.sleep(1)


    def __transmit_data(self, data: bytes):
        self.__midi_char.notify(None, data)
    

