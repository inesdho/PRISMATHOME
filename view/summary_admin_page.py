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


class SummaryAdmin:
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
    @brief The show_page function creates and displays all the elements of the "summary" page
    @param the instance
    @return Nothing
    """
    def show_page(self):
        # Frame that will contain the title of the page and the data about the observation
        self.frame = ttk.Frame(self.master)
        self.frame.pack(fill=tk.BOTH)

        # Title of the page
        title_label = ttk.Label(self.frame, text='Summary', font=16)
        title_label.pack(pady=10)

        # Information about the configuration
        scenario_frame = ttk.Frame(self.frame)
        scenario_frame.pack(fill=tk.BOTH)
        scenario_label = ttk.Label(scenario_frame, text="Scenario : " + globals.global_scenario_name_configuration, padding=10)
        scenario_label.pack(side=tk.LEFT)

        # Creation of the frame that will contain the buttons
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(padx=5, pady=10)

        # Connect to the database and retrieve sensor types
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="prismathome"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT id_type, type FROM sensor_type")
            all_sensor_types = cursor.fetchall()

            for sensor_type_id, sensor_type in all_sensor_types:
                sensor_type_button = ttk.Button(
                    button_frame,
                    text=sensor_type,
                    command=lambda id=sensor_type_id, type=sensor_type: self.display_sensor_info(id, type),
                    padding=5
                )
                sensor_type_button.pack(side=tk.LEFT)

            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            print(f"Error: {err}")

        # Creation of the frame that will contain the datas relative to the sensors
        self.sensor_text = tk.Text(self.frame)
        self.sensor_text.pack(fill=tk.BOTH, expand=tk.TRUE)

    """!
    @brief This function displays into the text widget all the sensors of a type selected by the user and the infos
    related to the sensors
    @param the instance
    sensor_type_id -> the id of the type of sensor that needs it's info dipalyed
    sensor_type -> the type of sensor
    @return Nothing
    """
    def display_sensor_info(self, sensor_type_id, sensor_type):

        # Anabeling the edition of the text widget and clearing it's previous content
        self.sensor_text.configure(state='normal')
        self.sensor_text.delete("1.0", tk.END)

        sensor_count = globals.sensor_counts.get(sensor_type_id, 0)
        entries_for_type = [entry for entry in globals.global_sensor_entries if entry[0] == sensor_type_id]
        if not entries_for_type:
            self.sensor_text.insert(tk.END, f"No information available for {sensor_type} sensors.\n")
        else:
            for index, (sensor_id, label_entry, description_entry) in enumerate(entries_for_type, start=1):
                if index > sensor_count:
                    break
                sensor_info = f"{sensor_type} sensor {index}:\nLabel: {label_entry}\nDescription: {description_entry}\n\n"
                self.sensor_text.insert(tk.END, sensor_info)

        # Disabeling the edition once the modifications are done
        self.sensor_text.configure(state='disabled')

    """!
    @brief This functions clears the entire "new observation" page
    @param the instance
    @return Nothing
    """
    def clear_page(self):
        self.frame.destroy()

    """!
    @brief This functions validated all the infos relative to the current created configuration in order to save them
    @param the instance
    @return Nothing
    """
    def validate_conf(self):
        # Connect to the database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="prismathome"
        )
        cursor = conn.cursor()

        # Exécutez une requête
        query = "INSERT INTO configuration (id_config, id_user, label, description)VALUES(%s, %s, %s, %s)"
        cursor.execute(query, (
        globals.global_id_config, globals.global_id_user, globals.global_scenario_name_configuration,
        globals.global_description_configuration))
        conn.commit()

        # Insert each sensor's data into the database
        for sensor_type_id, label, description in globals.global_sensor_entries:
            query = "INSERT INTO sensor_config (id_config, id_sensor_type, sensor_label, sensor_description) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (globals.global_id_config, sensor_type_id, label, description))

        conn.commit()
        cursor.close()
        conn.close()
