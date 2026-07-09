from .button import switch
class ButtonHandler:
    def __init__(self):
        
        
        self.buttons = [
            (4, switch.create(4, self.switch_callback), 0),
            (5, switch.create(5, self.switch_callback), 1),
            (6, switch.create(6, self.switch_callback), 2),
            (7, switch.create(7, self.switch_callback), 3)
        ] 
          # this is really not very organised but it works more stable than anything else...
          # also not very readable (If you havent read any other parts of this code) 
        
    
    def switch_callback(self, pin: int):
        for button in self.buttons:
            if button[0] == pin:
                print(f"Button of pin {button[0]}, aka button {button[2]} pressed.")
                
                break

    
