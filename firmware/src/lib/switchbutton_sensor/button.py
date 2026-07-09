from machine import Pin # type: ignore
import time


class switch:
    def __init__(self, pin, handler, debounce_ms=150):
        self.pin = pin
        self.handler = handler
        self.debounce_ms = debounce_ms
        self.last_press = 0

        self.button = Pin(pin, Pin.IN, Pin.PULL_UP)

        self.button.irq(
            trigger=Pin.IRQ_FALLING,
            handler=self._irq
        )

    def _irq(self, pin):
        now = time.ticks_ms()

        if time.ticks_diff(now, self.last_press) < self.debounce_ms:
            return

        self.last_press = now
        self.handler(self.pin)
    
    @classmethod # means its a factory method for code validation before returning a valid object. instead returns none if faliure. 
    def create(self, pin: int, handler: callable):
        if not handler: 
            return None 
        if not isinstance(pin, int):
            return None
   
        return switch(pin, handler)

        
        
    

