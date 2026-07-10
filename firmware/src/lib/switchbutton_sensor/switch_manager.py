from .button import switch
from ..debug.debug import DPrint
class SwitchMgr:
    def __init__(self, cb_MidiQueueAdd: callable):
        
        self.__ParentHandler = cb_MidiQueueAdd
        self.buttons = [
            (4, switch.create(4, self.switch_callback), 0), # should be the correct config for all modules. 
            (5, switch.create(5, self.switch_callback), 1), # however, for my build of the hardware, ports on GPIO 4/5 are switched. 
            (6, switch.create(6, self.switch_callback), 2), # update: fixed. corresponds correctly. 
            (7, switch.create(7, self.switch_callback), 3)
        ] 
          # this is really not very organised but it works more stable than anything else...
          # instantiates all of the switches usingf the factory method provided (callback validation)
        
    
    def switch_callback(self, pin: int, note_down: bool):
        for button in self.buttons:
            if button[0] == pin: 
                DPrint(f"Button of pin {button[0]}, aka button {button[2]} {'pressed' if note_down else 'released'}.")
                self.__ParentHandler((button[2], note_down))
                break

    
