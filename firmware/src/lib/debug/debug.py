import sys
import select # type: ignore


DEBUGMODE = True


def wait_for_mpremote():
    print("Waiting for mpremote... Press Ctrl+C to skip.")

    while True:
        r, _, _ = select.select([sys.stdin], [], [], 0.1)

        if r:
            sys.stdin.read(1)  # consume whatever triggered it
            print("Connection activity detected. Handing over.")
            return