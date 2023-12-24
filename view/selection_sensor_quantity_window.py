import tkinter as tk
from tkinter import ttk
from tkinter import *
import globals

class QuantitySensor:
    def __init__(self, master):
        self.master = master
        self.frame = ttk.Frame(self.master)

    def show_page(self):

        # Create a main frame which will be centered in the window
        self.frame = ttk.Frame(self.master)
        self.frame.pack(expand=True)

        # Create a frame for the sensor selectors inside the main frame
        self.frame_sensors = tk.Frame(self.frame, padx=10, pady=10)
        self.frame_sensors.pack()

        # Function to create a labeled frame with a ComboBox inside
        def create_sensor_frame(master, text, var):
            sensor_frame = tk.LabelFrame(master, text=text, padx=5, pady=5)
            # Create a ttk combobox and store it in the instance variable
            combobox = ttk.Combobox(sensor_frame, values=[0, 1, 2, 3, 4, 5], state="readonly", width=5, textvariable=var)
            combobox.set(0)  # set the default value
            combobox.pack(padx=10, pady=5)
            return sensor_frame

        # Create StringVars for each sensor type
        self.presence_var = tk.StringVar()
        self.opening_var = tk.StringVar()
        self.activity_var = tk.StringVar()
        self.pressure_var = tk.StringVar()

        # Create and pack the sensor frames
        presence_sensor_frame = create_sensor_frame(self.frame_sensors, "Presence sensor", self.presence_var)
        presence_sensor_frame.pack(side=tk.LEFT, padx=10)

        opening_sensor_frame = create_sensor_frame(self.frame_sensors, "Opening sensor", self.opening_var)
        opening_sensor_frame.pack(side=tk.LEFT, padx=10)

        activity_sensor_frame = create_sensor_frame(self.frame_sensors, "Activity sensor", self.activity_var)
        activity_sensor_frame.pack(side=tk.LEFT, padx=10)

        pressure_sensor_frame = create_sensor_frame(self.frame_sensors, "Pressure sensor", self.pressure_var)
        pressure_sensor_frame.pack(side=tk.LEFT, padx=10)

    def clear_page(self):
        self.frame.destroy()
        self.frame_sensors.destroy()

    def on_next_button_click(self):
        # Retrieve values from the StringVars
        globals.num_presence_sensors= self.presence_var.get()
        globals.num_opening_sensors = self.opening_var.get()
        globals.num_activity_sensors = self.activity_var.get()
        globals.num_pressure_sensors = self.pressure_var.get()

        # Print the values
        print("Number of Presence Sensors selected:", globals.num_presence_sensors)
        print("Number of Opening Sensors selected:", globals.num_opening_sensors)
        print("Number of Activity Sensors selected:", globals.num_activity_sensors)
        print("Number of Pressure Sensors selected:", globals.num_pressure_sensors)
