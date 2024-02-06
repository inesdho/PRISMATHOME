"""!
@file modify_or_create_configuration_page.py
@brief This file will contain all the widgets and functions related to the "create or modify a configuration"
page itself
@author Naviis-Brain
@version 1.0
@date
"""
import tkinter as tk
from tkinter import ttk

import globals
from model import local

from utils.entry_manager import EntryManager
from utils.text_manager import TextManager

class ModifyOrCreateConfiguration:

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
        self.frame.pack(fill=tk.BOTH, expand=True)

    def show_page(self):
        """!
        @brief The show_page function creates and displays all the elements of the "create or modify a configuration" page
        @param self : the instance
        @return Nothing
        """
        # Left Frame for configuration modification
        self.left_frame = tk.Frame(self.master, bd=2, relief="sunken", padx=5, pady=5)
        self.left_frame.place(relx=0.02, rely=0.09, relwidth=0.46, relheight=0.50)

        # Displays the title of the page
        label_title_left = ttk.Label(self.left_frame, text="MODIFY A CONFIGURATION", font=globals.global_font_title, foreground='#3daee9')
        label_title_left.pack(pady=10)

        # Creates the elements related to the selection of a configuration to modify
        label_configuration_label = tk.Label(self.left_frame, text="Configuration :", font=globals.global_font_title1)
        label_configuration_label.pack(anchor="nw")

        # Get the configuration labels and ids
        configurations = local.get_configurations('1')

        if configurations is not None:
            # Creation of a tuple list
            self.configuration_values = [(config[2], config[0]) for config in configurations]

            # Creation of a combobox with the list of configuration labels
            self.configuration_combobox = ttk.Combobox(self.left_frame, state="readonly", width=30, background="white")
            self.configuration_combobox['values'] = [label for label, id_config in self.configuration_values]
            self.configuration_combobox.set(self.configuration_values[0][0])
            self.configuration_combobox.pack(fill="x", pady=10)
        else:
            configurations = ['No configuration available']
            self.configuration_combobox = ttk.Combobox(self.left_frame, state="readonly", values=configurations, width=29)
            self.configuration_combobox.set(configurations[0])
            self.configuration_combobox.pack(fill="x", pady=10)

        # Right Frame for configuration Creation
        self.right_frame = tk.Frame(self.master, bd=2, relief="sunken", padx=5, pady=5)
        self.right_frame.place(relx=0.50, rely=0.09, relwidth=0.48, relheight=0.50)

        # Displays the title of the page
        label_title_right = ttk.Label(self.right_frame, text="CREATE A CONFIGURATION", font=globals.global_font_title, foreground='#3daee9')
        label_title_right.pack(pady=10)

        # Creates the elemtents related to the creation of a new configuration
        tk.Label(self.right_frame, text="Configuration label :", font=globals.global_font_title1).pack(anchor="nw")
        self.right_frame.update()
        self.configuration_label_entry = EntryManager(self.right_frame, min=1, max=30, has_width=self.right_frame.winfo_width())

        tk.Label(self.right_frame, text="Description :", font=globals.global_font_title1).pack(anchor="nw")
        # Create a Text widget for multi-line text entry
        self.configuration_description_text = TextManager(self.right_frame, min=1, max=800,
                                                          has_width=self.right_frame.winfo_width(),
                                                          has_height=5)

    def save_label_description_id_of_config_into_globals(self):
        """!
        @brief This function is called when the user clicks on a button to create a new configuration and saves the
        label of the new configuration and its description into global variables.
        @param self : the instance
        @return Nothing
        """

        # Saving the variables into global variables
        globals.global_scenario_name_configuration = self.configuration_label_entry.get()
        globals.global_description_configuration = self.configuration_description_text.get()

    def clear_page(self):
        """!
        @brief This function clears the entire "new observation" page
        @param self : the instance
        @return Nothing
        """
        # Destroy the frame
        self.frame.destroy()
        self.right_frame.destroy()
        self.left_frame.destroy()


    def get_selected_id_config(self):
        """
       @brief Retrieves the 'id_config' associated with the selected label in the combobox.

       @return The 'id_config' associated with the selected label in the combobox.
               Returns None if no item is selected or if the selected item is not found.
       """
        selected_label = self.configuration_combobox.get()
        for label, id_config in self.configuration_values:
            if label == selected_label:
                return id_config
        return None

    def start_config_modification(self):
        """!
        @brief This function saves the config to modify and the sensors associated to the configuration into global
        variables
        @param self : the instance
        @return Nothing
        """
        # Store the selected config into a global variable
        globals.global_id_config_modify = self.get_selected_id_config()
        globals.global_label_modify, globals.global_description_modify = local.get_config_labels_description_ids(
            globals.global_id_config_modify)
        globals.sensor_counts.clear()

        # Get the list of sensor associated with the configuration
        list_sensor_config = local.get_sensors_from_configuration(globals.global_id_config_modify)

        # Get the list of sensor types
        sensor_types = local.get_sensor_type_list()

        # Count the number of sensor of each type and add it to the sensor_count global and add each sensor in the
        # global_sensor_entries global variable
        for id_sensor_type, type_sensor in sensor_types:
            count = 0
            for index, sensor in enumerate(list_sensor_config, start=0):
                if type_sensor == sensor["type"]:
                    globals.global_sensor_entries.append((id_sensor_type, sensor["label"], sensor["description"], f"{id_sensor_type}_{count}"))
                    count = count + 1
            globals.sensor_counts.setdefault(id_sensor_type, []).append(count)

