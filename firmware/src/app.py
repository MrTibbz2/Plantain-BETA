from lib.debug.debug import DPrint
import lib.pl_bluetooth.pl_bluetooth
import lib.switchbutton_sensor.switch_manager
from collections import deque
class App: # container class for handling all operations between subsystems gracefully. 
    def __init__(self):
        
        self.__ble = lib.pl_bluetooth.pl_bluetooth.ble()
        self.__buttonIndex = lib.pl_bluetooth.pl_bluetooth.ButtonIndex()
        self.__midi = lib.pl_bluetooth.pl_bluetooth.MIDI(self.__ble, self.__buttonIndex)
        self.__switchMgr = lib.switchbutton_sensor.switch_manager.SwitchMgr()
        self.MIDIQueue = deque()
        
    def run(self):
        pass





