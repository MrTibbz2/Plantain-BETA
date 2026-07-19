import asyncio
from lib.debug.debug import wait_for_mpremote, DEBUGMODE, DPrint
from app import App

# waits for serial conn and enter press before running actual application.
if DEBUGMODE:
    wait_for_mpremote()
    DPrint("Debug mode enabled.")
    DPrint("Running application...")

app = App(wifi_ssid="Arecibomessage", wifi_password="Dumb@Black&WhiteCat9")
asyncio.run(app.run())

