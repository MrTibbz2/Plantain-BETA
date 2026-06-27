from lib.pl_bluetooth.pl_bluetooth import ble
import asyncio
from lib.debug.debug import wait_for_mpremote, DEBUGMODE



ble_device = ble()



# waits for serial conn and enter press before running actual application.
if DEBUGMODE:
    wait_for_mpremote()
    print("Debug mode enabled.")

    
print("Running application...")
asyncio.run(ble_device.run())