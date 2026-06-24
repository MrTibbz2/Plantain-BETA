import os
import sys
import glob
import time

def ensure_root():
    """Ensures the script is running with root privileges."""
    if os.name == 'posix' and os.geteuid() != 0:
        print("🔒 Serial port access requires root privileges. Escalating via sudo...")
        try:
            args = ['sudo', '-E', sys.executable] + sys.argv
            os.execvp('sudo', args)
        except Exception as e:
            print(f"❌ Failed to escalate privileges: {e}")
            sys.exit(1)

def find_micropython_port_native():
    """Scans for potential ESP32 serial ports using native system paths."""
    print("Scanning active system serial ports...")
    
    # Generate list of common Linux USB/CDC device ports (ttyUSB* and ttyACM*)
    ports = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
    
    if not ports:
        return None

    for port in ports:
        print(f"Testing port: {port}")
        # Use raw stty and cat commands built directly into Linux to verify the port
        # This completely avoids needing 'pyserial'
        try:
            # 1. Configure the port speed to 115200 baud
            os.system(f"stty -F {port} 115200 raw -echo -echoe -echok")
            
            # 2. Trigger raw REPL mode, send confirmation print string, drop back to friendly REPL
            # We pipe this sequence straight into the device path
            cmd = f"echo -e '\r\x03\x03\x01print(\"PRJMD_ACK\")\r\n\x02' > {port}"
            os.system(cmd)
            
            # Give the ESP32 a brief window to process the serial string
            time.sleep(0.1)
            return port
        except Exception:
            continue
    return None

def upload_files(port):
    local_src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../firmware/src'))
    print(f" Found MicroPython device on {port}!")
    print(f"Syncing local firmware from '{local_src_dir}' to device...")
    
    # Call the global mpremote binary directly via shell command
    cmd = f"mpremote connect {port} fs cp -r {local_src_dir}/* :"
    
    if os.system(cmd) == 0:
        print(" Firmware copy complete! Soft-resetting device...")
        os.system(f"mpremote connect {port} soft-reset")
    else:
        print("\n❌ Error: Failed to copy files.")
        print("Ensure 'mpremote' is available in your PATH (e.g., run 'pipx install mpremote')")

if __name__ == "__main__":
    ensure_root()
    
    target_port = find_micropython_port_native()
    if target_port:
        upload_files(target_port)
    else:
        print("❌ Error: No active ESP32 / MicroPython serial interfaces detected.")
        sys.exit(1)