"""!
@file labellisation_sensor_page.py
@brief This file will contain all the widgets and functions related to the "labellisation sensor" page itself
@author Naviis-Brain
@version 1.0
@date
"""
import tkinter as tk
from tkinter import ttk
import mysql.connector
from model import local
import globals
from controller.entry_manager import EntryManager

class LabelisationSensor:
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
        self.sensor_entries = []  # List to hold the label, description entries for each sensor, and sensor type ID

        self.frame.pack(fill=tk.BOTH, expand=tk.TRUE)

        # Displays the title of the page
        label = ttk.Label(self.frame, text="Sensor labellisation", font=globals.global_font_title, padding=10)
        label.pack(pady=20)

        # Creation of a canvas in order to add a scrollbar in case to many lines of sensors are displayed
        self.canvas = tk.Canvas(self.frame, bd=2, relief="ridge", highlightthickness=2)
        self.scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill="y")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.frame_canvas = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), anchor='nw', window=self.frame_canvas)

    def show_page(self):
        """!
        @brief The show_page function creates and displays all the elements of the "labellisation sensor" page
        @param self : the instance
        @return Nothing
        """

        # Create entries for the sensors using the data from globals.sensor_counts
        for sensor_type_id, quantity in globals.sensor_counts.items():
            for i in range(quantity):
                # Create a unique id for each sensor
                unique_id = f"{sensor_type_id}_{i}"

                # Find the previous values entered if they are any
                existing_entry = next((entry for entry in globals.global_sensor_entries if entry[3] == unique_id), None)

                # Check if the previous values exist
                initial_label = existing_entry[1] if existing_entry else "Label"
                initial_description = existing_entry[2] if existing_entry else "Description"

                sensor_type = local.get_sensor_type_from_id_type(sensor_type_id)

                if sensor_type:
                    label_text = f'{sensor_type} sensor {i+1}'
                else:
                    label_text = 'Unknown sensor'
                    sensor_type_id = None

                # Give sensor_type_id to the method create_labeled_entry
                self.create_labeled_entry(i, sensor_type_id, label_text, initial_label, initial_description)

        # Configure the scroll region to follow the content of the frame
        self.frame_canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def create_labeled_entry(self, i, sensor_type_id, label_text, initial_label, initial_description):
        """!
        @brief This function creates label entries according to the sensor quantity of each type selected by the user in the
        selection sensor quantity page. The user can then enter the label and descrition to attribute to each sensor
        @param self : the instance
        @param i : which number of sensor for this type of sensor is this sensor
        @param sensor_type_id : the id of the type of sensor
        @param label_text : the label of the sensor, sensor_type_id
        @param initial_label : the label to display on the initialisation of the page
        @param initial_description : the description to display on the initialisation of the page
        @return Nothing
        """
        entry_frame = ttk.Frame(self.frame_canvas)
        entry_frame.pack(pady=5, fill=tk.BOTH, expand=tk.TRUE)

        label = ttk.Label(entry_frame, text=label_text, width=20)
        label.pack(side=tk.LEFT)

        label_label = ttk.Label(entry_frame, text="Label :", width=10, font=globals.global_font_text)
        label_label.pack(side=tk.LEFT)
        entry_label = EntryManager(entry_frame, min=1, max=80, has_width=20, auto_pack=False, default_text=initial_label)
        entry_label.get_entry().pack(side=tk.LEFT)

        description_label = ttk.Label(entry_frame, text="Description :", width=15, font=globals.global_font_text)
        description_label.pack(side=tk.LEFT)
        entry_description = EntryManager(entry_frame, min=1, max=600, has_width=80, has_special_char=True, auto_pack=False,
                                         default_text=initial_description)
        entry_description.get_entry().pack(side=tk.LEFT)

        unique_id = f"{sensor_type_id}_{i}"

        # Add the sensor_type_id to the list of sensor_entries with the label and description
        self.sensor_entries.append((sensor_type_id, entry_label, entry_description, unique_id))

    def get_sensor_data(self):
        """!
        @brief This function saves the label and description entered by the user for each sensor into global variables
        @param the instance
        @return Nothing
        """
        globals.global_sensor_entries.clear()
        # Iterate through the sensor_entries list and print the label and description for each sensor
        for sensor_type_id, label_entry, description_entry, unique_id in self.sensor_entries:
            label = label_entry.get()
            description = description_entry.get()
            globals.global_sensor_entries.append((sensor_type_id, label, description, unique_id))

    def clear_page(self):
        """!
        @brief This functions clears the entire "new observation" page
        @param the instance
        @return Nothing
        """
        self.frame.destroy()
