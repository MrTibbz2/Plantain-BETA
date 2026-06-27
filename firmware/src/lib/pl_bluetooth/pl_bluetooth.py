import asyncio
import aioble # type: ignore | only available on mp.
import bluetooth # type: ignore
from .uuids import MIDI_SERVICE_UUID, MIDI_CHAR_UUID
import json 
import io # type: ignore
import os
from ..debug.debug import DPrint


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
        DPrint("registered device name as:", name)
    
    
    async def run(self):
        while True:
            async with await aioble.advertise(
                100_000,
                name=self.__device_name,
                services=[self.MIDI_SERVICE_UUID],
            ) as connection:
                self.__connection = connection
                DPrint(f"connected to device.")
                while connection.is_connected():
                    try:
                        pass
                        # tx = bytearray([0x80, 0x80, 0x90, 0x3C, 0x64])
                        # self.__midi_char.notify(self.__connection, tx)
                    except:
                        pass
                    await asyncio.sleep_ms(100)
                self.__connection = None
                DPrint(f"device disconnected.")


    def __transmit(self, data: bytes):
        if self.__connection and self.__connection.is_connected():
            self.__midi_char.notify(self.__connection, data)


class MidiNote:
    def __init__(self, note, velocity=100, channel=0, state=0):
        self.note = note & 0x7F
        self.velocity = velocity & 0x7F
        self.channel = channel & 0x0F
        self.state = state  # 0 = off, 1 = on

    def dump(self):
        # returns a bytearray representing the note state
        # simple packed format: [status, note, velocity]
        # status encodes channel + on/off

        status = 0x90 | (self.channel & 0x0F) if self.state else 0x80 | (self.channel & 0x0F)

        return bytearray((status, self.note, self.velocity))


class ButtonIndex: 
    # class for storing, writing and editing configs for what buttons map to what midi notes.
    # 
    # example config for one note:
    #     {
    #         "button": 0,
    #         "note": 60,
    #         "velocity": 100,
    #     }.
    # buttons 0-3 are usable. 
    
    CONFIG_DIR = "/configs"
    CONFIG_EXT = ".pl_conf"

    def __init__(self):
        self.__current_button_to_note_index = [] # the config loaded currently.
        if not os.path.exists(self.CONFIG_DIR):
            os.makedirs(self.CONFIG_DIR)
    
    def __validate_config_path(self, filename: str) -> str:
        """Validate filename and return safe full path. Prevents path injection."""
        if not filename.endswith(self.CONFIG_EXT):
            filename += self.CONFIG_EXT
        
        # Remove any path separators to prevent directory traversal
        filename = filename.replace("/", "").replace("\\", "")
        
        full_path = os.path.join(self.CONFIG_DIR, filename)
        
        # Verify resolved path is within CONFIG_DIR
        resolved = os.path.normpath(full_path)
        config_dir_resolved = os.path.normpath(self.CONFIG_DIR)
        
        if not resolved.startswith(config_dir_resolved):
            raise ValueError(f"Invalid config path: {filename}")
        
        return full_path

    def load_config(self, filename: str):
        path = self.__validate_config_path(filename)
        with open(path, "r") as f:
            self.__current_button_to_note_index = json.load(f)
    
    def save_config(self, filename: str):
        path = self.__validate_config_path(filename)
        with open(path, "w") as f:
            json.dump(self.__current_button_to_note_index, f)
    
    def delete_config(self, filename: str):
        path = self.__validate_config_path(filename)
        os.remove(path)
    
    def button_to_note(self, button_number: int, state=1):
        for item in self.__current_button_to_note_index:
            if item["button"] == button_number:
                return MidiNote(
                    note=item["note"], 
                    velocity=item.get("velocity", 100), 
                    state=state
                    )
        return None

    

class MIDI:
    def __init__(self, ble: ble, buttonIndex: ButtonIndex):
        self.__ble = ble
        self.__ButtonIndex = buttonIndex

    def note_on(self, button_number: int):
        note = self.__ButtonIndex.button_to_note(button_number, state=1)
        if note:
            self.__ble.__transmit(note.dump())
    def note_off(self, button_number: int):
        note = self.__ButtonIndex.button_to_note(button_number, state=0)
        if note:
            self.__ble.__transmit(note.dump())


    

    
