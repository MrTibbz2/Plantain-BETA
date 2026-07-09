from lib.pl_bluetooth.pl_bluetooth import ble, ButtonIndex, MIDI
import asyncio
import time
from lib.debug.debug import wait_for_mpremote, DEBUGMODE,DPrint
from lib.switchbutton_sensor.button import switch
from firmware.src.lib.switchbutton_sensor.switch_manager import SwitchMgr


ble_device = ble()
button_index = ButtonIndex()


# waits for serial conn and enter press before running actual application.
if DEBUGMODE:
    wait_for_mpremote()
    DPrint("Debug mode enabled.")
    DPrint("Running application...")




bh = SwitchMgr()
while True:


    DPrint("running...")
    time.sleep(1)
#asyncio.run(ble_device.run())