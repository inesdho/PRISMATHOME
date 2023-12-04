import tkinter as tk
from tkinter import ttk


class QuantitySensor:
    def __init__(self, master):
        self.master = master
        self.frame = ttk.Frame(self.master)

    def show_page(self):
        # Create a main frame which will be centered in the window
        self.frame_main = tk.Frame(self.master)
        self.frame_main.pack(expand=True)

        # Create a frame for the sensor selectors inside the main frame
        self.frame_sensors = tk.Frame(self.frame_main, padx=10, pady=10)
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

        # Create a frame for the buttons below the sensor selectors
        self.frame_buttons = tk.Frame(self.frame_main)
        self.frame_buttons.pack(pady=5)

        # Add buttons
        btn_back = tk.Button(self.frame_buttons, text="Back")
        btn_back.pack(side=tk.LEFT, padx=10, expand=True)

        btn_next = tk.Button(self.frame_buttons, text="Next", command=self.on_next_button_click)
        btn_next.pack(side=tk.RIGHT, padx=10, expand=True)

    def clear_page(self):
        self.frame.destroy()

    def on_next_button_click(self):
        # Retrieve values from the StringVars
        presence_value = self.presence_var.get()
        opening_value = self.opening_var.get()
        activity_value = self.activity_var.get()
        pressure_value = self.pressure_var.get()

        # Print the values
        print("Number of Presence Sensors selected:", presence_value)
        print("Number of Opening Sensors selected:", opening_value)
        print("Number of Activity Sensors selected:", activity_value)
        print("Number of Pressure Sensors selected:", pressure_value)
