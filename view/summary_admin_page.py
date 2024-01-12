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

    def show_page(self):
        """!
        @brief The show_page function creates and displays all the elements of the "summary" page
        @param self : the instance
        @return Nothing
        """
        # Frame that will contain the title of the page and the data about the observation
        self.frame = ttk.Frame(self.master)
        self.frame.pack(fill=tk.BOTH)

        # Title of the page
        title_label = ttk.Label(self.frame, text='Summary', font=16)
        title_label.pack(pady=10)

        # Information about the configuration
        scenario_frame = ttk.Frame(self.frame)
        scenario_frame.pack(fill=tk.BOTH)
        scenario_label = ttk.Label(scenario_frame, text="Configuration : " + globals.global_scenario_name_configuration, padding=10)
        scenario_label.pack(side=tk.LEFT)

        # Creation of the frame that will contain the buttons
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(padx=5, pady=10)

        # Connect to the database and retrieve sensor types
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Q3fhllj2",
                database="prisme_home_1"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT id_type, type FROM sensor_type")
            all_sensor_types = cursor.fetchall()

            for sensor_type_id, sensor_type in all_sensor_types:
                # Convert sensor_type_id to str for comparison
                sensor_type_id_str = str(sensor_type_id)
                # Filter entries for this sensor type
                entries_for_type = [
                    entry for entry in globals.global_sensor_entries
                    if str(entry[0]).startswith(sensor_type_id_str)  # Ensure both are strings
                ]
                if entries_for_type.count()==0:
                    sensor_type_button = ttk.Button(
                        button_frame,
                        text=sensor_type,
                        command=lambda id=sensor_type_id, type=sensor_type: self.display_sensor_info(id, type),
                        padding=5
                    )
                    sensor_type_button.pack(side=tk.LEFT, padx=5)

            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            print(f"Error: {err}")

        # Creation of the frame that will contain the datas relative to the sensors
        self.sensor_text = tk.Text(self.frame)
        self.sensor_text.pack(fill=tk.BOTH, expand=tk.TRUE)

    def display_sensor_info(self, sensor_type_id, sensor_type):
        """!
        @brief This function display the infos related to the chosen sensor type inside the text widget.
        @param self : the instance
        @param sensor_type_id : id related to the type of sensor
        @param sensor_type :  label of the type of sensor
        @return Nothing
        """
        self.sensor_text.configure(state='normal')
        self.sensor_text.delete("1.0", tk.END)

        # Convert sensor_type_id to str for comparison
        sensor_type_id_str = str(sensor_type_id)
        sensor_count = globals.sensor_counts.get(sensor_type_id, 0)

        # Filter entries for this sensor type
        entries_for_type = [
            entry for entry in globals.global_sensor_entries
            if str(entry[0]).startswith(sensor_type_id_str)  # Ensure both are strings
        ]

        for index, (sensor_id, label_entry, description_entry) in enumerate(entries_for_type, start=1):
            if index > sensor_count:
                break
            sensor_info = f"{sensor_type} sensor {index}:\nLabel: {label_entry}\nDescription: {description_entry}\n\n"
            self.sensor_text.insert(tk.END, sensor_info)

        self.sensor_text.configure(state='disabled')

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
        # Connect to the database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Q3fhllj2",
            database="prisme_home_1"
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

