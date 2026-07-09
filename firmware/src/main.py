from lib.pl_bluetooth.pl_bluetooth import ble, ButtonIndex, MIDI
import asyncio
import time
from lib.debug.debug import wait_for_mpremote, DEBUGMODE
from lib.switchbutton_sensor.button import switch
from lib.switchbutton_sensor.port_handler import ButtonHandler


ble_device = ble()
button_index = ButtonIndex()


# waits for serial conn and enter press before running actual application.
if DEBUGMODE:
    wait_for_mpremote()
    print("Debug mode enabled.")


print("Running application...")

bh = ButtonHandler()
while True:
    print("running...")
    time.sleep(1)
#asyncio.run(ble_device.run())