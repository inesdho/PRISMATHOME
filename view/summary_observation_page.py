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


class SummaryObservation:
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

    def show_page(self, ):
        """!
        @brief The show_page function creates and displays all the elements of the "summary" page
        @param the instance
        @param is_observation : True if the page is to be displayed in the context of an observation
        @return Nothing
        """
        # Frame that will contain the title of the page and the data about the observation
        self.frame = ttk.Frame(self.master)
        self.frame.pack(fill=tk.BOTH)

        # Title of the page
        title_label = ttk.Label(self.frame, text='Summary running observation', font=16)
        title_label.pack(pady=10)

        # Information about the configuration
        scenario_frame = ttk.Frame(self.frame)
        scenario_frame.pack(fill=tk.BOTH)
        # TODO ajouter la valeur de scenario
        scenario_label = ttk.Label(scenario_frame,
                                   text="Scenario : " + self.get_scenario(globals.global_new_id_observation),
                                   padding=10)
        scenario_label.pack(side=tk.LEFT)

        session_frame = ttk.Frame(self.frame)
        session_frame.pack(fill=tk.BOTH)
        session_label = ttk.Label(session_frame,
                                  text="Session : " + self.get_session(globals.global_new_id_observation), padding=10)
        session_label.pack(side=tk.LEFT)

        participant_frame = ttk.Frame(self.frame)
        participant_frame.pack(fill=tk.BOTH)
        participant_label = ttk.Label(participant_frame,
                                      text="Participant : " + self.get_participant(globals.global_new_id_observation),
                                      padding=10)
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
        sensor_infos = self.get_sensor_infos_for_type(sensor_type_id)

        if not sensor_infos:
            self.sensor_text.insert(tk.END, f"No information available for {sensor_type} sensors.\n")
        else:
            for sensor_info in sensor_infos:
                sensor_label = sensor_info[0]
                sensor_description = sensor_info[1]
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

    def stop_observation(self):
        # TODO voir avec les indus comment recuperer et inserer les datas
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Q3fhllj2",
                database="prisme_home_1"
            )
            cursor = conn.cursor()

            # Execute a request
            query_update = "UPDATE prisme_home_1.observation SET active=0 WHERE id_observation=%s"
            cursor.execute(query_update, (globals.global_new_id_observation,))  # Pass label as a tuple
            conn.commit()

        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            return None

        finally:
            # Closing the cursor and connection
            cursor.close()
            conn.close()

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

    def get_sensor_infos_for_type(self, sensor_type_id):
        """ Retrieves sensor information for a specific type from the database. """
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Q3fhllj2",
                database="prisme_home_1"
            )
            cursor = conn.cursor()

            query = "SELECT label, description FROM sensor WHERE id_type=%s AND id_observation=%s"
            cursor.execute(query, (sensor_type_id, globals.global_new_id_observation))

            sensor_infos = cursor.fetchall()

            cursor.close()
            conn.close()
            return sensor_infos

        except mysql.connector.Error as err:
            print(f"Database error: {err}")
        return []
