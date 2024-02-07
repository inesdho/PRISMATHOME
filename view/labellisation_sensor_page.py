"""!
@file labellisation_sensor_page.py
@brief This file will contain all the widgets and functions related to the "labellisation sensor" page itself
@author Naviis-Brain
@version 1.0
@date
"""
import tkinter as tk
from tkinter import ttk
from model import local
from utils import globals
from utils.entry_manager import EntryManager

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
        label = ttk.Label(self.frame, text="SENSOR LABELLISATION", font=globals.global_font_title, foreground='#3daee9')
        label.pack(pady=30)

        # Creation of a canvas in order to add a scrollbar in case to many lines of sensors are displayed
        self.canvas = tk.Canvas(self.frame, bd=2, relief="ridge", highlightthickness=2)
        self.scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill="y")
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5)
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
                initial_label = existing_entry[1] if existing_entry else ""
                initial_description = existing_entry[2] if existing_entry else ""

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

        label = ttk.Label(entry_frame, text=label_text, width=20, font=globals.global_font_title1)
        label.pack(side=tk.LEFT, padx=5)

        label_label = ttk.Label(entry_frame, text="Label :", width=10, font=globals.global_font_text, anchor='center')
        label_label.pack(side=tk.LEFT)
        entry_label = EntryManager(entry_frame, min=1, max=80, has_width=20, auto_pack=False, default_text=initial_label)
        entry_label.get_entry().pack(side=tk.LEFT)

        description_label = ttk.Label(entry_frame, text="Description :", width=15, font=globals.global_font_text, anchor='center')
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

    def are_all_field_filled(self):
        """!
        @brief This functions checks that all the entry are filled
        @param the instance
        @return True if all the entry are filled, else return false
        """
        for sensor_type_id, label_entry, description_entry, unique_id in self.sensor_entries:
            if label_entry.get() == "":
                return False
            if description_entry.get() == "":
                return False
        return True

    def are_all_label_unique(self):
        """!
        @brief This functions checks that all the entry label are unique
        @param the instance
        @return True if all the entry are unique, else return false
        """
        for sensor_type_id_i, label_entry_i, description_entry_i, unique_id_i in self.sensor_entries:
            for sensor_type_id_j, label_entry_j, description_entry_j, unique_id_j in self.sensor_entries:
                # If the labels are identical and if it's not the same sensor return False
                if label_entry_i.get() == label_entry_j.get():
                    if unique_id_i != unique_id_j:
                        return False
        # Return True if all the labels are identical
        return True

    def are_label_not_only_numbers(self):
        """!
       @brief This functions checks that each the entry label doesn't contain only number
       @param the instance
       @return False if no entry contain only number, else return True
       """
        for sensor_type_id, label_entry, description_entry, unique_id in self.sensor_entries:
            # Checks each label to know if they are only digits
            if label_entry.get().isdigit():
                return False
        # Return True if no label contains only digits
        return True