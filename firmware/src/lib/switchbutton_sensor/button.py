from machine import Pin # type: ignore
import time


class switch:
    def __init__(self, pin, handler, debounce_ms=100):
        self.pin = pin
        self.handler = handler
        self.debounce_ms = debounce_ms
        self.last_press = 0
        self.last_release = 0
        self.last_state = None

        self.button = Pin(pin, Pin.IN, Pin.PULL_UP)

        self.button.irq(
            trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING,
            handler=self._irq
        )

    def _irq(self, pin): 
        
        # this method contains a large  amount of debounce logic. 
        # this is required to ensure that off and on logic is handled nicely and bounces are not sent. 
        # state of last click is stored to ensure that there is an off for every on. 
        now = time.ticks_ms()
        note_down = not self.button.value()

        if note_down == self.last_state:
            return

        if note_down and time.ticks_diff(now, self.last_press) < self.debounce_ms:
            return
        if not note_down and time.ticks_diff(now, self.last_release) < self.debounce_ms:
            return

        if note_down:
            self.last_press = now
        else:
            self.last_release = now

        self.last_state = note_down
        self.handler(self.pin, note_down)
    
    @classmethod # means its a factory method for code validation before returning a valid object. instead returns none if faliure. 
    def create(cls, pin: int, handler: callable):
        if not handler: 
            return None 
        if not isinstance(pin, int):
            return None
   
        return switch(pin, handler)

        
        
    

