import tkinter as tk
from tkinter import ttk
import pandas as pd
from pymodbus.client import ModbusTcpClient
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time
import socket

# Dictionary of register addresses and their names
registers = {
    'AIN0': 0,
    'AIN1': 2,
    'AIN2': 4,
    'AIN3': 6
    # Add other registers as necessary
}


# Create the data frame for holding register values
data_frame = pd.DataFrame(columns=registers.keys())
data_frame.set_index(list(registers.keys()))

# Function to read the registers
def read_registers(client: ModbusTcpClient):
    data = {}
    for name, address in registers.items():
        rr = client.read_holding_registers(address, 2)  # Reading holding registers
        if rr.isError():
            data[name] = None
        else:
            data[name] = data_to_float32(rr.registers)
    return data


# Function to update the GUI with new register values
def update_values(client, data_frame, graphs, x_data):
    while True:
        data = read_registers(client)
        df = pd.DataFrame([data])
        data_frame = pd.concat([data_frame, df], ignore_index=True)
        print(data_frame.tail())

        # Append new x value for the time axis
        x_data.append(x_data[-1] + 0.5 if x_data else 0)  # Increment time by 0.5s

        # Update the live graph for each register
        for key, line in graphs.items():
            y_data = list(line.get_ydata())  # Get existing y-data
            y_data.append(df[key].values[0])    # Append the new value
            line.set_ydata(y_data)              # Update y-data for the line
            line.set_xdata(x_data)              # Update x-data for the line

        # Adjust x and y limits to match the data
        plt.xlim([max(0, x_data[-1] - 10), x_data[-1] + 1])  # Keep a moving window of 10 seconds
        plt.ylim([0, 10000])  # Adjust y-limits as needed based on your register values

        # Save the DataFrame to a CSV file every 5 seconds (or as needed)
        data_frame.to_csv('data/data.csv', index=False)

        # Redraw the canvas for live update
        plt.draw()
        time.sleep(.5)


# Function to start Modbus client and GUI updates
def start_modbus(ip, canvas, data_frame, graphs):
    client = ModbusTcpClient(ip, port=5021, timeout=5)
    x_data = []  # This will hold the x-axis (time) values
    if client.connect():
        print("Connected to device")
        threading.Thread(target=update_values, args=(client, data_frame, graphs, x_data), daemon=True).start()
    else:
        print("Failed to connect to device")


# Main function to create the GUI
def create_gui():
    # Set up Tkinter window
    root = tk.Tk()
    root.title("LabJack T7 Pro Register Monitor")

    # Entry for IP address
    ip_label = ttk.Label(root, text="Enter IP Address:")
    ip_label.grid(row=0, column=0, padx=5, pady=5)
    
    ip_entry = ttk.Entry(root)
    ip_entry.insert(0, socket.gethostbyname(socket.gethostname()))
    ip_entry.grid(row=0, column=1, padx=5, pady=5)

    # Button to start reading registers
    start_button = ttk.Button(root, text="Start", command=lambda: start_modbus(ip_entry.get(), canvas, data_frame, graphs))
    start_button.grid(row=0, column=2, padx=5, pady=5)

    # Create the matplotlib figure for live plotting
    fig, ax = plt.subplots(figsize=(6, 4))
    graphs = {}
    for key in registers.keys():
        line, = ax.plot([], [], label=key)
        graphs[key] = line

    ax.legend(loc='upper right')
    ax.set_title('Live Register Values')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Register Values')

    # Integrate matplotlib with Tkinter
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().grid(row=1, column=0, columnspan=3)

    root.protocol("WM_DELETE_WINDOW", window_exit)
    
    root.mainloop()

def window_exit():
    print("bye")
    # data_frame.to_csv('data\data.csv')
    exit()



# Helper function to convert data to float32
def data_to_float32(data):
    return float(data[0]) + (float(data[1]) / (1 << 16))

# Run the GUI
if __name__ == "__main__":
    create_gui()

def save_data():
    data_frame.to_csv('data\data.csv')
