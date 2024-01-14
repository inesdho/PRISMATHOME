"""!
@file summary_admin_page.py
@brief This file will contain all the widgets and functions related to the "summary" page itself
@author Naviis-Brain
@version 1.0
@date
"""
import tkinter as tk
from tkinter import ttk
from tkinter import *
import globals
import mysql.connector
from model import local


class SummaryUser:
    def __init__(self, master):
        """!
        @brief The __init__ function sets the master frame in parameters as the frame that will contain all the widgets of
        this page
        @param self : the instance
        @param master : master frame (created in the controller.py file)
        @return Nothing
        """
        self.master = master
        self.frame = ttk.Frame(self.master)
        self.frame.pack(fill=tk.BOTH)

    def show_page(self):
        """!
        @brief The show_page function creates and displays all the elements of the "summary" page
        @param self : the instance
        @param is_observation : True if the page is to be displayed in the context of an observation
        @return Nothing
        """
        # Title of the page
        title_label = ttk.Label(self.frame, text='Summary', font=16)
        title_label.pack(pady=10)

        # Information about the configuration
        scenario_frame = ttk.Frame(self.frame)
        scenario_frame.pack(fill=tk.BOTH)
        # TODO ajouter la valeur de scenario
        scenario_label = ttk.Label(scenario_frame,
                                   text="Configuration : "
                                        + local.get_config_label_from_observation_id(globals.global_new_id_observation),
                                   padding=10)
        scenario_label.pack(side=tk.LEFT)

        session_frame = ttk.Frame(self.frame)
        session_frame.pack(fill=tk.BOTH)
        session_label = ttk.Label(session_frame,
                                  text="Session : "
                                       + local.get_observation_info(globals.global_new_id_observation,
                                                                    'session_label'),
                                  padding=10)
        session_label.pack(side=tk.LEFT)

        participant_frame = ttk.Frame(self.frame)
        participant_frame.pack(fill=tk.BOTH)
        participant_label = ttk.Label(participant_frame,
                                      text="Participant : "
                                           + local.get_observation_info(globals.global_new_id_observation,
                                                                        'participant'),
                                      padding=10)
        participant_label.pack(side=tk.LEFT)

        # Creation of the frame that will contain the buttons
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(padx=5, pady=10)

        # retrieve sensor types
        try:
            all_sensor_types = local.get_sensor_type_list()

            for sensor_type_id, sensor_type in all_sensor_types:
                sensor_type_button = ttk.Button(
                    button_frame,
                    text=sensor_type,
                    command=lambda id=sensor_type_id, type=sensor_type: self.display_sensor_info(id, type),
                    padding=5
                )
                sensor_type_button.pack(side=tk.LEFT)

        except mysql.connector.Error as err:
            print(f"Error: {err}")

        # Creation of the frame that will contain the datas relative to the sensors
        self.sensor_text = tk.Text(self.frame)
        self.sensor_text.pack(fill=tk.BOTH, expand=tk.TRUE)

    def display_sensor_info(self, sensor_type_id, sensor_type):
        """!
        @brief Displays information about all sensors of a selected type in the text widget.
        @param self: Instance reference.
        @param sensor_type_id: ID of the sensor type whose information is to be displayed.
        @param sensor_type: Type of sensor.
        @return None
        """
        self.sensor_text.configure(state='normal')
        self.sensor_text.delete("1.0", tk.END)

        # Retrieve information from sensors of this type from the database
        sensor_infos = local.get_sensor_info_from_observation(globals.global_new_id_observation, sensor_type_id)

        if not sensor_infos:
            self.sensor_text.insert(tk.END, f"No information available for {sensor_type} sensors.\n")
        else:
            for sensor_info in sensor_infos:
                sensor_label = sensor_info['label']
                sensor_description = sensor_info['description']
                sensor_display = f"{sensor_type} sensor:\nLabel: {sensor_label}\nDescription: {sensor_description}\n\n"
                self.sensor_text.insert(tk.END, sensor_display)

        self.sensor_text.configure(state='disabled')

    def clear_page(self):
        """!
        @brief This functions clears the entire "new observation" page
        @param self : the instance
        @return Nothing
        """
        self.frame.destroy()


    def clear_sensor_entries(self):
        """!
        @brief This function clears the sensor entries after validation.
        """
        globals.global_sensor_entries.clear()
        for _, label_entry, description_entry in globals.global_sensor_entries:
            label_entry.set('')
            description_entry.set('')
