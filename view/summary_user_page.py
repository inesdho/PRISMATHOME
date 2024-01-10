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
        scenario_label = ttk.Label(scenario_frame, text="Configuration : " + self.get_scenario(globals.global_new_id_observation), padding=10)
        scenario_label.pack(side=tk.LEFT)

        session_frame = ttk.Frame(self.frame)
        session_frame.pack(fill=tk.BOTH)
        session_label = ttk.Label(session_frame, text="Session : " + self.get_session(globals.global_new_id_observation), padding=10)
        session_label.pack(side=tk.LEFT)

        participant_frame = ttk.Frame(self.frame)
        participant_frame.pack(fill=tk.BOTH)
        participant_label = ttk.Label(participant_frame, text="Participant : " + self.get_participant(globals.global_new_id_observation), padding=10)
        participant_label.pack(side=tk.LEFT)

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
            cursor.execute("SELECT DISTINCT id_type, type FROM sensor_type")    # get_sensor_type_list()
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
        """!
        @brief This function displays into the text widget all the sensors of a type selected by the user and the infos
        related to the sensors
        @param self : the instance
        @param sensor_type_id : the id of the type of sensor that needs it's info dipalyed
        @param sensor_type : the type of sensor
        @return Nothing
        """

        # Anabeling the edition of the text widget and clearing it's previous content
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

        # Disabeling the edition once the modifications are done
        self.sensor_text.configure(state='disabled')

    def clear_page(self):
        """!
        @brief This functions clears the entire "new observation" page
        @param self : the instance
        @return Nothing
        """
        self.frame.destroy()

    def validate_conf(self):
        # TODO: virer du controller et faire un appel à model.create_configuration et model.save_sensor_configs
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

    def get_session(self, id_observation):
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Q3fhllj2",
                database="prisme_home_1"
            )
            cursor = conn.cursor()

            # Execute a request
            query = "SELECT session_label FROM observation WHERE id_observation=%s"
            cursor.execute(query, (id_observation,))  # Pass label as a tuple

            # Fetch the first result
            result = cursor.fetchone()

            # Make sure to fetch all results to clear the cursor before closing it, even if you don't use them.
            while cursor.fetchone() is not None:
                pass

            return result[0] if result else None

        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            return None

        finally:
            # Closing the cursor and connection
            cursor.close()
            conn.close()

    def get_participant(self, id_observation):
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Q3fhllj2",
                database="prisme_home_1"
            )
            cursor = conn.cursor()

            # Execute a request
            query = "SELECT participant FROM observation WHERE id_observation=%s"
            cursor.execute(query, (id_observation,))  # Pass label as a tuple

            # Fetch the first result
            result = cursor.fetchone()

            # Make sure to fetch all results to clear the cursor before closing it, even if you don't use them.
            while cursor.fetchone() is not None:
                pass

            return result[0] if result else None

        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            return None

        finally:
            # Closing the cursor and connection
            cursor.close()
            conn.close()

    def get_scenario(self, id_observation):
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Q3fhllj2",
                database="prisme_home_1"
            )
            cursor = conn.cursor()

            # Execute a request
            query = "SELECT configuration.label FROM configuration, observation WHERE observation.id_config=configuration.id_config AND observation.id_observation=%s"
            cursor.execute(query, (id_observation,))  # Pass label as a tuple

            # Fetch the first result
            result = cursor.fetchone()

            # Make sure to fetch all results to clear the cursor before closing it, even if you don't use them.
            while cursor.fetchone() is not None:
                pass

            return result[0] if result else None

        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            return None

        finally:
            # Closing the cursor and connection
            cursor.close()
            conn.close()
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
