# NOTE: THESE SCRIPTS ARE WRITTEN WITH AI. they are not part of the functional code that affects the user. they are used by me alone. 
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
    
    # Generate list of common Linux USB/CDC device ports
    ports = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
    
    if not ports:
        return None

    for port in ports:
        print(f"Testing port: {port}")
        try:
            # 1. Configure port parameters to 115200 baud
            os.system(f"stty -F {port} 115200 raw -echo -echoe -echok")
            
            # 2. Probe REPL state to check responsiveness
            cmd = f"echo -e '\r\x03\x03\x01print(\"PRJMD_ACK\")\r\n\x02' > {port}"
            os.system(cmd)
            
            time.sleep(0.1)
            return port
        except Exception:
            continue
    return None

def dump_files(port):
    dump_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), './dump'))
    
    if not os.path.exists(dump_dir):
        os.makedirs(dump_dir)
        print(f"Created local backup folder: {dump_dir}")

    print(f" Found MicroPython device on {port}!")
    print(f"Pulling all files from target device into {dump_dir}...")
    
    # Recursively copy all files from device root (:) to local dump/ folder
    cmd = f"mpremote connect {port} fs cp -r : {dump_dir}"
    
    if os.system(cmd) == 0:
        print(f"  Success! All storage files backed up cleanly inside {dump_dir}/")
    else:
        print("\n❌ Error: Backup extraction failed.")
        print("Ensure 'mpremote' is accessible in your PATH.")

if __name__ == "__main__":
    ensure_root()
    
    target_port = find_micropython_port_native()
    if target_port:
        dump_files(target_port)
    else:
        print("❌ Error: No active ESP32 / MicroPython serial interfaces detected.")
        sys.exit(1)