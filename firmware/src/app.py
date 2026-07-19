from lib.debug.debug import DPrint
import lib.pl_bluetooth.pl_bluetooth
import lib.switchbutton_sensor.switch_manager
from collections import deque
import asyncio
import lib.web.web
class App: # container class for handling all operations between subsystems gracefully. 
    def __init__(self):
        self.__web = lib.web.web.Web()
        self.__ble = lib.pl_bluetooth.pl_bluetooth.ble()
        self.__buttonIndex = lib.pl_bluetooth.pl_bluetooth.ButtonIndex()
        self.__midi = lib.pl_bluetooth.pl_bluetooth.MIDI(self.__ble, self.__buttonIndex)
        self.__switchMgr = lib.switchbutton_sensor.switch_manager.SwitchMgr(self.MIDIQ_append_cb)
        self.MIDIQueue = deque([], 8)
        
        
    
    def MIDIQ_append_cb(self, i):
        self.MIDIQueue.append(i)
        if len(self.MIDIQueue) > 7:
            DPrint("WARNING: MIDIQueue is overflowing. consider a different approach long term. (mate youre fucked)")

    async def run(self):
        await asyncio.gather(
            self.__ble.run(),
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



