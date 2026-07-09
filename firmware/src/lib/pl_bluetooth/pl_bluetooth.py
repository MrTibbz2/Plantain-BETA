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


class MidiNote: # storage object for a singular midi note. 
    def __init__(self, note, velocity=100, channel=0, state=0):
        self.note = note & 0x7F
        self.velocity = velocity & 0x7F
        self.channel = channel & 0x0F
        self.state = state  # 0 = off, 1 = on

    def dump(self):
        # returns the bytes that a midi interpreter will accept over BLE. 

        status = 0x90 | (self.channel & 0x0F) if self.state else 0x80 | (self.channel & 0x0F)

        return bytearray((status, self.note, self.velocity))


class ButtonIndex:
    CONFIG_DIR = "/configs"
    CONFIG_EXT = ".pl_conf"
    DEFAULT_CONFIG = "default"
    DEFAULT_NOTES = [60, 62, 64, 67]

    def __init__(self):
        self.__current_button_to_note_index = []

        try:
            os.stat(self.CONFIG_DIR)
        except OSError:
            os.mkdir(self.CONFIG_DIR)

        self.__ensure_default_config()
        self.load_config(self.DEFAULT_CONFIG)

    def __ensure_default_config(self): # makes sure there is a default config. to make sure theres a fallback. 
        default_path = self.CONFIG_DIR + "/" + self.DEFAULT_CONFIG + self.CONFIG_EXT

        try:
            os.stat(default_path)
            return
        except OSError:
            pass

        try:
            default_config = [
                {"button": i, "note": self.DEFAULT_NOTES[i], "velocity": 100}
                for i in range(4)
            ]

            with open(default_path, "w") as f:
                json.dump(default_config, f)

            DPrint("Default config created")

        except Exception as e:
            DPrint(f"Error creating default config: {e}")

    def __validate_config_path(self, filename: str) -> str: # checks the config path for path escapement/injection 
        if not filename.endswith(self.CONFIG_EXT):
            filename += self.CONFIG_EXT

        if "/" in filename or "\\" in filename:
            raise ValueError("Invalid filename")

        if filename == f"{self.DEFAULT_CONFIG}{self.CONFIG_EXT}":
            raise ValueError("Cannot modify default config")

        return self.CONFIG_DIR + "/" + filename

    def load_config(self, filename: str) -> bool: # loads the.. config???? 
        try:
            if not filename.endswith(self.CONFIG_EXT):
                filename += self.CONFIG_EXT

            path = self.CONFIG_DIR + "/" + filename

            with open(path, "r") as f:
                self.__current_button_to_note_index = json.load(f)

            return True

        except FileNotFoundError:
            DPrint(f"Config file not found: {filename}")
            return False

        except Exception as e:
            DPrint(f"Error loading config: {e}")
            return False

    def save_config(self, filename: str) -> bool: # shoves the config into filesystem. 
        try:
            path = self.__validate_config_path(filename)

            with open(path, "w") as f:
                json.dump(self.__current_button_to_note_index, f)

            return True

        except ValueError as e:
            DPrint(f"Invalid config path: {e}")
            return False

        except Exception as e:
            DPrint(f"Error saving config: {e}")
            return False

    def delete_config(self, filename: str) -> bool:
        try:
            path = self.__validate_config_path(filename)
            os.remove(path)
            return True

        except ValueError as e:
            DPrint(f"Invalid config path: {e}")
            return False

        except FileNotFoundError:
            DPrint(f"Config file not found: {filename}")
            return False

        except Exception as e:
            DPrint(f"Error deleting config: {e}")
            return False

    def button_to_note(self, button_number: int, state=1):
        for item in self.__current_button_to_note_index:
            if item["button"] == button_number:
                return MidiNote(
                    note=item["note"],
                    velocity=item.get("velocity", 100),
                    state=state,
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