"""!
@file summary_page.py
@brief This file will contain all the widgets and functions related to the "summary" page itself
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


class SummaryAdmin:
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
        label = ttk.Label(self.frame, text="SUMMARY ADMIN", font=globals.global_font_title, foreground='#3daee9')
        label.pack(pady=30)

        if globals.global_id_config_modify:
            # Information about the configuration
            scenario_label = ttk.Label(self.frame, text="Configuration : " + local.get_config_labels_ids(globals.global_id_config_modify),
                                       padding=10, anchor="w", font=globals.global_font_title1)
            scenario_label.pack(pady=20, fill=tk.BOTH)
        else:
            # Information about the configuration
            scenario_label = ttk.Label(self.frame, text="Configuration : " + globals.global_scenario_name_configuration,
                                       padding=10, anchor="w", font=globals.global_font_title1)
            scenario_label.pack(pady=20, fill=tk.BOTH)

        # Creation of the frame that will contain the buttons
        self.button_frame = ttk.Frame(self.frame)
        self.button_frame.pack(padx=5, pady=10)

        # Creation of a canvas in order to add a scrollbar in case to many lines of sensors are displayed
        self.canvas = tk.Canvas(self.frame, bd=2, relief="ridge", highlightthickness=2)
        self.scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill="y")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.frame_canvas = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), anchor='nw', window=self.frame_canvas)

        # Creation of the frame tate will contain the title of the field
        frame_title = ttk.Frame(self.frame_canvas)
        frame_title.pack(pady=5, fill=tk.BOTH, expand=tk.TRUE)

        # Create the title of the different field
        ttk.Label(frame_title, background="#3daee9", width=20, text="Sensor", borderwidth=0.5, relief="solid",
                  padding=5, anchor="center", font=globals.global_font_text).pack(side=tk.LEFT)
        ttk.Label(frame_title, background="#3daee9", width=20, text="Label", borderwidth=0.5, relief="solid",
                  padding=5, anchor="center", font=globals.global_font_text).pack(side=tk.LEFT)
        ttk.Label(frame_title, background="#3daee9", width=80, text="Description", borderwidth=0.5, relief="solid",
                  padding=5, anchor="center", font=globals.global_font_text).pack(side=tk.LEFT)

        self.data_frame = ttk.Frame(self.frame_canvas)
        self.data_frame.pack(pady=5, fill=tk.BOTH, expand=tk.TRUE)

    def show_page(self):
        """!
        @brief The show_page function creates and displays all the elements of the "summary" page
        @param self : the instance
        @return Nothing
        """
        # Get the sensor types from DB
        all_sensor_types = local.get_sensor_type_list()

        # TODO ines/mathilde : Commenter, code pas compréhensible et fait planter les requêtes
        for sensor_type_id, sensor_type in all_sensor_types:

            print("globals.global_sensor_entries : ",globals.global_sensor_entries)

            # Convert sensor_type_id to str for comparison
            sensor_type_id_str = str(sensor_type_id)
            # Filter entries for this sensor type
            entries_for_type = [
                entry for entry in globals.global_sensor_entries
                if str(entry[0]).startswith(sensor_type_id_str)  # Ensure both are strings
            ]

            print("entries_for_type = ",entries_for_type)

            if entries_for_type:
                sensor_type_button = ttk.Button(
                    self.button_frame,
                    text=sensor_type,
                    command=lambda type=sensor_type, entries_for_type=entries_for_type: self.display_sensor_info(type, entries_for_type),
                    padding=5
                )
                sensor_type_button.pack(side=tk.LEFT, padx=5)

    def display_sensor_info(self, sensor_type, entries_for_type):
        """!
        @brief Displays information about all sensors of a selected type.
        @param self: Instance reference.
        @param entries_for_type: all the sensors associated with a type of sensor
        @param sensor_type: Type of sensor.
        @return None
        """

        self.data_frame.destroy()

        self.data_frame = ttk.Frame(self.frame_canvas)
        self.data_frame.pack(pady=5, fill=tk.BOTH, expand=tk.TRUE)

        for index, (sensor_id, label_entry, description_entry, id_unique) in enumerate(entries_for_type, start=1):
            sensor_frame = ttk.Frame(self.data_frame)
            sensor_frame.pack(pady=5, fill=tk.BOTH, expand=tk.TRUE)

            # Showing the type of the sensor
            ttk.Label(sensor_frame, text=f"{sensor_type} sensor {index}", width=20, anchor='w', wraplength=140,
                      background="white", borderwidth=0.5, relief="solid", padding=5, font=globals.global_font_text).pack(side=tk.LEFT)

            # Creating a text widget tht will contain the label associated with the sensor
            ttk.Label(sensor_frame, text=f"{label_entry}", borderwidth=0.5, background="white", width=20,
                      relief="solid", padding=5, font=globals.global_font_text).pack(side=tk.LEFT)

            # Showing the description of the sensor
            ttk.Label(sensor_frame, text=f"{description_entry}", borderwidth=0.5, background="white", width=80,
                      relief="solid", padding=5, font=globals.global_font_text).pack(side=tk.LEFT)

        # Configure the scroll region to follow the content of the frame
        self.frame_canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def clear_page(self):
        """!
        @brief This functions clears the entire "summary admin" page
        @param self : the instance
        @return Nothing
        """
        self.data_frame.destroy()
        self.frame_canvas.destroy()
        self.canvas.destroy()
        self.frame.destroy()
        self.button_frame.destroy()

    def validate_conf_for_create(self):
        """!
        @brief This functions validated all the infos relative to the current created configuration in order to save them
        @param self : the instance
        @return Nothing
        """

        # Get the new id config to create it
        globals.global_id_config = local.get_new_config_id()

        # Remove the id_unique field in the sensor list which is useless
        new_sensor_entries = [(sensor_id, label_entry, description_entry)
                              for index, (sensor_id, label_entry, description_entry, id_unique)
                              in enumerate(globals.global_sensor_entries, start=1)]
        # Insert the configuration in DB and the sensor configs
        local.create_configuration(globals.global_id_config,
                                   globals.global_id_user,
                                   globals.global_scenario_name_configuration,
                                   globals.global_description_configuration,
                                   new_sensor_entries)
        self.clear_sensor_entries_and_sensor_count()

    def validate_conf_for_modify(self):
        """!
        @brief This functions validated all the infos relative to the current created configuration in order to save them
        @param self : the instance
        @return Nothing
        """
        local.update_configuration_active('0', globals.global_id_config_modify)
        globals.global_id_config_modify = local.get_new_config_id()

        # Remove the id_unique field in the sensor list which is useless
        new_sensor_entries = [(sensor_id, label_entry, description_entry)
                              for index, (sensor_id, label_entry, description_entry, id_unique)
                              in enumerate(globals.global_sensor_entries, start=1)]
        # Insert the configuration in DB and the sensor configs
        #local.insert_new_sensors_for_configuration(globals.global_id_config, new_sensor_entries)
        local.create_configuration(globals.global_id_config_modify,
                                   globals.global_id_user,
                                   globals.global_label_modify,
                                   globals.global_description_modify,
                                   new_sensor_entries)
        self.clear_sensor_entries_and_sensor_count()


    def clear_sensor_entries_and_sensor_count(self):
        """!
        @brief This function clears the sensor entries after validation.
        """
        globals.global_sensor_entries.clear()
        globals.sensor_counts.clear()
        # Vous pouvez également effacer les entrées visuelles ici, si nécessaire
        for _, label_entry, description_entry in globals.global_sensor_entries:
            label_entry.set('')
            description_entry.set('')

