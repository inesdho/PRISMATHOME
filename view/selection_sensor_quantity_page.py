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
import globals
import mysql.connector

class QuantitySensor:
    """!
    @brief The __init__ function sets the master frame in parameters as the frame that will contain all the widgets of
    this page
    @param the instance, the master frame (created in the controller.py file)
    @return Nothing
    """
    def __init__(self, master):
        self.master = master
        self.frame = ttk.Frame(self.master)

    """!
    @brief This functions connects to the database and fetch all the existing sensor type
    @param the instance
    @return all the sensors type in the database
    """
    def fetch_sensor_types(self):

        # Connexion to the database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Q3fhllj2",
            database="prisme_home_1"
        )
        cursor = conn.cursor()

        # Execute a request
        cursor.execute("SELECT id_type, type FROM sensor_type")  # Adaptez cette requête à votre BDD
        return cursor.fetchall()

    """!
    @brief The show_page function creates and displays all the elements of the "selection sensor quantity" page
    @param the instance
    @return Nothing
    """
    def show_page(self):

        # Create a main frame which will be centered in the window
        self.frame = ttk.Frame(self.master)
        self.frame.pack(expand=True)

        # Create a frame for the sensor selectors inside the main frame
        self.frame_sensors = tk.Frame(self.frame, padx=10, pady=10)
        self.frame_sensors.pack()

        # Calls a function to fetch all the existing sensor types in the database
        sensor_types = self.fetch_sensor_types()

        # Creating comboboxes according to the types of sensors existing
        self.sensor_vars = {}  # Stocking the labels of the sensor type
        for id, type in sensor_types:
            sensor_frame = tk.LabelFrame(self.frame_sensors, text=type, padx=5, pady=5)
            sensor_var = tk.StringVar()
            combobox = ttk.Combobox(sensor_frame, values=[0, 1, 2, 3, 4, 5], state="readonly", width=5,
                                    textvariable=sensor_var)
            combobox.set(0)  # Valeur par défaut
            combobox.pack(padx=10, pady=5)
            sensor_frame.pack(side=tk.LEFT, padx=10)
            self.sensor_vars[id] = sensor_var  # Stockez la variable pour une utilisation ultérieure

    """!
    @brief This functions clears the entire "new observation" page
    @param the instance
    @return Nothing
    """
    def clear_page(self):
        self.frame.destroy()
        self.frame_sensors.destroy()

    """!
    @brief This function saves the quantity of sensors for each type of sensor that the user selected into global 
    variables
    @param the instance
    @return Nothing
    """
    def on_next_button_click(self):
        globals.sensor_counts.clear()

        # Récupérez les valeurs des StringVars et les stockez dans le dictionnaire sensor_counts de globals
        for sensor_type, sensor_var in self.sensor_vars.items():
            globals.sensor_counts[sensor_type] = int(sensor_var.get())

        # Imprimez les valeurs pour vérifier
        for sensor_type, count in globals.sensor_counts.items():
            print(f"Number of id_type {sensor_type} Sensors selected:", count)