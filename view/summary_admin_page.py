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

        # Creation of the frame that will contain the buttons
        self.button_frame = ttk.Frame(self.master)
        self.button_frame.pack(padx=5, pady=10)

        # Displays the title of the page
        label = ttk.Label(self.frame, text="Summary", font=globals.global_font_title, padding=10)
        label.pack(pady=20)

        # Information about the configuration
        scenario_label = ttk.Label(self.frame, text="Configuration : " + globals.global_scenario_name_configuration,
                                   padding=10, anchor="w", font=globals.global_font_title1)
        scenario_label.pack(pady=20, fill=tk.BOTH)

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
        ttk.Label(frame_title, background="lightgrey", width=20, text="Sensor", borderwidth=1, relief="solid",
                  padding=5, font=globals.global_font_text, anchor="center").pack(side=tk.LEFT)
        ttk.Label(frame_title, background="lightgrey", width=20, text="Label", borderwidth=1, relief="solid",
                  padding=5, font=globals.global_font_text, anchor="center").pack(side=tk.LEFT)
        ttk.Label(frame_title, background="lightgrey", width=80, text="Description", borderwidth=1, relief="solid",
                  padding=5, font=globals.global_font_text, anchor="center").pack(side=tk.LEFT)

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

        for sensor_type_id, sensor_type in all_sensor_types:
                # Convert sensor_type_id to str for comparison
                sensor_type_id_str = str(sensor_type_id)
                # Filter entries for this sensor type
                entries_for_type = [
                    entry for entry in globals.global_sensor_entries
                    if str(entry[0]).startswith(sensor_type_id_str)  # Ensure both are strings
                ]
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

        for index, (sensor_id, label_entry, description_entry) in enumerate(entries_for_type, start=1):
            sensor_frame = ttk.Frame(self.data_frame)
            sensor_frame.pack(pady=5, fill=tk.BOTH, expand=tk.TRUE)

            # Showing the type of the sensor
            ttk.Label(sensor_frame, text=f"{sensor_type} sensor {index}", width=20, anchor='w', wraplength=140,
                      background="white", borderwidth=1, relief="solid", padding=5).pack(side=tk.LEFT)

            # Creating a text widget tht will contain the label associated with the sensor
            ttk.Label(sensor_frame, text=f"{label_entry}", borderwidth=1, background="white", width=20,
                      relief="solid", padding=5).pack(side=tk.LEFT)

            # Showing the description of the sensor
            ttk.Label(sensor_frame, text=f"{description_entry}", borderwidth=1, background="white", width=80,
                      relief="solid", padding=5).pack(side=tk.LEFT)

        # Configure the scroll region to follow the content of the frame
        self.frame_canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def clear_page(self):
        """!
        @brief This functions clears the entire "new observation" page
        @param self : the instance
        @return Nothing
        """
        self.frame.destroy()

    def validate_conf(self):
        """!
        @brief This functions validated all the infos relative to the current created configuration in order to save them
        @param self : the instance
        @return Nothing
        """

        # Get the new id config to create it
        globals.global_id_config = local.get_new_config_id()

        # Insert the configuration in DB
        local.create_configuration(globals.global_id_config,
                                   globals.global_id_user,
                                   globals.global_scenario_name_configuration,
                                   globals.global_description_configuration)

        # Insert each sensor's data into the database
        local.create_sensor_configs(globals.global_id_config, globals.global_sensor_entries)

        self.clear_sensor_entries()

    def clear_sensor_entries(self):
        """!
        @brief This function clears the sensor entries after validation.
        """
        globals.global_sensor_entries.clear()
        # Vous pouvez également effacer les entrées visuelles ici, si nécessaire
        for _, label_entry, description_entry in globals.global_sensor_entries:
            label_entry.set('')
            description_entry.set('')

