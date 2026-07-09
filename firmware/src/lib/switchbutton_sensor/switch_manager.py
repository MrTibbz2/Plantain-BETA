from .button import switch
from ..debug.debug import DPrint
class SwitchMgr:
    def __init__(self, cb_MidiQueueAdd):
        
        
        self.buttons = [
            (4, switch.create(4, self.switch_callback), 0),
            (5, switch.create(5, self.switch_callback), 1),
            (6, switch.create(6, self.switch_callback), 2),
            (7, switch.create(7, self.switch_callback), 3)
        ] 
          # this is really not very organised but it works more stable than anything else...
          # instantiates all of the switches usingf the factory method provided (callback validation)
        
    
    def switch_callback(self, pin: int):
        for button in self.buttons:
            if button[0] == pin:
                DPrint(f"Button of pin {button[0]}, aka button {button[2]} pressed.")
                
                
                break

    
