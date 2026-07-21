import asyncio
from lib.debug.debug import wait_for_mpremote, DEBUGMODE, DPrint
from app import App

# waits for serial conn and enter press before running actual application.
if DEBUGMODE:
    wait_for_mpremote()
    DPrint("Debug mode enabled.")
    DPrint("Running application...")

app = App(wifi_ssid="fedora-book", wifi_password="password")
asyncio.run(app.run())

