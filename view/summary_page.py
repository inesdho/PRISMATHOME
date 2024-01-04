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


class Summary:
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
    @param the instance, is_observation -> True if the page is to be displayed in the context of an observation
    @return Nothing
    """
    def show_page(self, is_observation):
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

        # The following information need to be display only if this page is called during an observation
        if is_observation:
            session_frame = ttk.Frame(self.frame)
            session_frame.pack(fill=tk.BOTH)
            session_label = ttk.Label(session_frame, text="Session : " + self.get_session(), padding=10)
            session_label.pack(side=tk.LEFT)

            participant_frame = ttk.Frame(self.frame)
            participant_frame.pack(fill=tk.BOTH)
            participant_label = ttk.Label(participant_frame, text="Participant : " + self.get_participant(), padding=10)
            participant_label.pack(side=tk.LEFT)

        # Creation of the frame that will contain the buttons
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(padx=5, pady=10)

        # Connect to the database and retrieve sensor types
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="prisme_home_1"
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

    def display_sensor_info(self, sensor_type_id, sensor_type):
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

        if not entries_for_type:
            self.sensor_text.insert(tk.END, f"No information available for {sensor_type} sensors.\n")
        else:
            for index, (sensor_id, label_entry, description_entry) in enumerate(entries_for_type, start=1):
                if index > sensor_count:
                    break
                sensor_info = f"{sensor_type} sensor {index}:\nLabel: {label_entry}\nDescription: {description_entry}\n\n"
                self.sensor_text.insert(tk.END, sensor_info)

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

    def get_session(self):
        # TODO Modifier la fonction pour qu'elle retourne la session de la configuration en cours
        return "Ceci est la session de l'observation"

    def get_participant(self):
        # TODO Modifier la fonction pour qu'elle retourne le particpant de la configuration en cours
        return "Ceci est le participant de l'observation"

    def exist_in_this_config(self, sensor_type):
        # TODO Modifier la fonction pour qu'elle retourne true si ce type de capteur est présent dans la configuration en cours sinon false
        return True

    def get_sensors_id_from_type(self, sensor_type):
        # TODO Modifier la fonction pour qu'elle retourne la liste des capteurs de type 'sensor_type' présent dans la configuration
        return ["id_sensor1", "id_sensor2", "id_sensor3", "id_sensor4", "id_sensor5", "id_sensor6"]

    def get_sensor_label(self, id_sensor):
        # TODO Modifier la fonction pour qu'elle retourne le label d'un capteur en fonction de son id
        return id_sensor + "sensor "

    def get_sensor_description(self, id_sensor):
        # TODO Modifier la fonction pour qu'elle retourne la description d'un capteur en fonction de son id
        return "Description du capteur " + id_sensor

    def get_sensor_status(self, id_sensor):
        # TODO Modifier la fonction pour qu'elle retourne le status d'un capteur en fonction de son id
        return "Status du capteur " + id_sensor
