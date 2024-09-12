import random
import time
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.server.async_io import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock
from threading import Thread

# Dictionary of register addresses and their names
registers = {
    'AIN0': 0,
    'AIN1': 2,
    'AIN2': 4,
    'AIN3': 6
    # Add other registers as necessary
}

# Function to update the registers with random values to simulate the device
def updating_writer(context: ModbusServerContext, registers):
    slave_id = 0x00  # Single slave ID, as we are using a single device
    while True:
        # Iterate through the registers and generate random values for each
        for register_name, register_address in registers.items():
            # Generate a random value for the current register
            value = int(random.uniform(0, 10) * 1000)
            # Update the holding registers (hr) with the value
            context[slave_id].setValues(3, register_address, [value])

        time.sleep(0.5)  # Update every 0.5 seconds

# Main function to start the simulated server
def run_simulated_device(static_ip):
    # Setup Modbus server information
    identity = ModbusDeviceIdentification()
    identity.VendorName = 'SimulatedLabjack'
    identity.ProductCode = 'T7Pro'
    identity.VendorUrl = 'http://simulated-labjack.com'
    identity.ProductName = 'Simulated LabJack T7 Pro'
    identity.ModelName = 'SimulatedModel'
    identity.MajorMinorRevision = '1.0'

    # Create context with holding registers (hr)
    store = ModbusSlaveContext(
        hr=ModbusSequentialDataBlock(0, [0] * 100)  # Simulate 100 holding registers
    )
    context = ModbusServerContext(slaves=store, single=True)

    # Start the register updater in a background thread
    updater = Thread(target=updating_writer, args=(context, registers))
    updater.start()

    # Bind the server to the static IP and port 5021
    StartTcpServer(context=context, identity=identity, address=(static_ip, 5021))

if __name__ == "__main__":
    # Replace this with the static IP address of your machine
    static_ip = "0.0.0.0"  # Replace with your machine's IP address
    run_simulated_device(static_ip)
