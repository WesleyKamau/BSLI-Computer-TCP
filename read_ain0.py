'''
This example reads AIN0 on a T7 at IP address 192.168.1.15 using pymodbus.

'''

# Import files
from convert_data import *
from pymodbus.client import ModbusTcpClient


# Open TCP port
client = ModbusTcpClient("192.168.1.2")

# Read AIN0
rr = client.read_input_registers(0, 2)
data_to_float32(rr.registers)
print("AIN0 = %.4f V" % data_to_float32(rr.registers))

# Close TCP port
client.close()
