"""!
@file selection_sensor_quantity_page.py
@brief This file will contain all the widgets and functions related to the "selection sensor quantity" page itself
@author Naviis-Brain
@version 1.0
@date
"""

import tkinter as tk
from tkinter import ttk
from tkinter import *
from model import local
import globals
import mysql.connector


class QuantitySensor:
    def __init__(self, master):
        """!
        @brief The __init__ function sets the master frame in parameters as the frame that will contain all the widgets of
        this page
        @param self : the instance
        @param master : the master frame (created in the controller.py file)
        @return Nothing
        """
        self.master = master
        self.frame = ttk.Frame(self.master)

    def show_page(self, is_modification):
        """!
        @brief The show_page function creates and displays all the elements of the "selection sensor quantity" page
        @param self : the instance
        @return Nothing
        """

        # Create a main frame which will be centered in the window
        self.frame = ttk.Frame(self.master)
        self.frame.pack(expand=True)

        # Displays the title of the page
        label = ttk.Label(self.frame, text="Sensor quantity selection", font=16)
        label.pack(pady=20)

        # Create a frame for the sensor selectors inside the main frame
        self.frame_sensors = tk.Frame(self.frame, padx=10, pady=10)
        self.frame_sensors.pack()

        if(is_modification):
            #TODO
            sensor_types = local.get_sensor_type_list()



        # Calls a function to fetch all the existing sensor types in the database
        sensor_types = local.get_sensor_type_list()

        # Creating comboboxes according to the types of sensors existing
        self.sensor_vars = {}  # Stocking the labels of the sensor type
        for id, type in sensor_types:
            sensor_frame = tk.LabelFrame(self.frame_sensors, text=type, padx=5, pady=5)
            sensor_var = tk.StringVar()
            combobox = ttk.Combobox(sensor_frame, values=[0, 1, 2, 3, 4, 5], state="readonly", width=5,
                                    textvariable=sensor_var)
            combobox.set(0)  # Default values
            combobox.pack(padx=10, pady=5)
            sensor_frame.pack(side=tk.LEFT, padx=10)
            self.sensor_vars[id] = sensor_var  # Stock the variable for a further use

    def clear_page(self):
        """!
        @brief This functions clears the entire "new observation" page
        @param self : the instance
        @return Nothing
        """
        self.frame.destroy()
        self.frame_sensors.destroy()

    def on_next_button_click(self):
        """!
        @brief This function saves the quantity of sensors for each type of sensor that the user selected into global
        variables
        @param self : the instance
        @return Nothing
        """
        globals.sensor_counts.clear()

        # Get the values of the StringVars and stock them into sensor_counts of globals
        for sensor_type, sensor_var in self.sensor_vars.items():
            globals.sensor_counts[sensor_type] = int(sensor_var.get())

        # Print the values to check
        for sensor_type, count in globals.sensor_counts.items():
            print(f"Number of id_type {sensor_type} Sensors selected:", count)

    def chose_at_least_one_sensor(self):
        """!
        @brief This function checks if the users has selected at least one sensor
        @param self : the instance
        @return true : if the user selected at least one sensor, false : if no sensor was selected
        """
        for sensor_type, sensor_var in self.sensor_vars.items():
            if int(sensor_var.get()) > 0:
                return True
        return False
