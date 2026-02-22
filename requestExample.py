import requests
import json
import time
from bacpypes.core import run, stop, deferred
from bacpypes.app import BIPSimpleApplication
from bacpypes.local.device import LocalDeviceObject
from bacpypes.object import BinaryOutputObject, AnalogInputObject

# -------------------------------
# Configuration
# -------------------------------
ARDUINO_IP = "192.168.137.50"  # Arduino server IP
POLL_INTERVAL = 0.5  # seconds

# BACnet Device
device = LocalDeviceObject(
    objectName="ArduinoBridge",
    objectIdentifier=1000,
    maxApduLengthAccepted=1024,
    segmentationSupported="noSegmentation",
    vendorIdentifier=15,
)

# BACnet Application
app = BIPSimpleApplication(device, "192.168.137.1/24")  # PC IP

# -------------------------------
# BACnet Objects
# -------------------------------
# LED object (BinaryOutput)
led_bo = BinaryOutputObject(
    objectIdentifier=("binaryOutput", 1), objectName="LED", presentValue=False
    
)

# Analog input object
sensor_ai = AnalogInputObject(
    objectIdentifier=("analogInput", 1), objectName="Analog0", presentValue=0.0
)

# Add objects to BACnet device
device.objectList = [led_bo, sensor_ai]


# -------------------------------
# Helper functions
# -------------------------------
def read_arduino():
    """Read Arduino JSON and print all values."""
    try:
        url = f"http://{ARDUINO_IP}"
        response = requests.get(url, timeout=1)
        data = response.json()

        # ----- Digital Outputs -----
        digital_out = data.get("Arduino Output Values", {}).get("Digital", {})
        print("Digital Outputs:")
        for pin, val in digital_out.items():
            print(f"  {pin}: {val}")

        # ----- Analog Outputs -----
        analog_out = data.get("Arduino Output Values", {}).get("Analog", {})
        print("Analog Outputs:")
        for pin, val in analog_out.items():
            print(f"  {pin}: {val}")

        # ----- Digital Inputs -----
        digital_in = data.get("Arduino Input Values", {}).get("Digital", {})
        print("Digital Inputs:")
        for pin, val in digital_in.items():
            print(f"  {pin}: {val}")

        print("-" * 30)

    except Exception as e:
        print(f"Error reading Arduino: {e}")


def write_arduino():
    """Write BACnet LED value back to Arduino."""
    try:
        led_state = "on" if led_bo.presentValue else "off"
        url = f"http://{ARDUINO_IP}/?led={led_state}"
        requests.get(url, timeout=0.5)
        print(f"[BACnet → Arduino] LED set to {led_state}")
    except Exception as e:
        print(f"Error writing Arduino: {e}")


# -------------------------------
# Main loop using BACpypes deferred
# -------------------------------
def poll_loop(arg=None):
    read_arduino()
    write_arduino()
    time.sleep(POLL_INTERVAL)  # pause 1 second between polls
    deferred(poll_loop)


# Start polling after BACpypes run
deferred(poll_loop)

# Run BACpypes core
try:
    print("BACnet bridge running...")
    run()
except KeyboardInterrupt:
    stop()
    print("BACnet bridge stopped.")
