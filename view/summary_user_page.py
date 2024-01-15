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
from model import local
import mysql.connector
import subprocess
import os
import signal
import threading
import model.local_mqtt


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
        self.sensor_entries = []  # List to hold the label, description entries for each sensor, and sensor type ID

        self.frame.pack(fill=tk.BOTH, expand=tk.TRUE)

        # Creation of the frame that will contain the buttons
        self.button_frame = ttk.Frame(self.master)
        self.button_frame.pack(padx=5, pady=10)

        # Displays the title of the page
        label = ttk.Label(self.frame, text="Summary", font=globals.global_font_title, padding=10)
        label.pack(pady=20)

        # Information about the configuration
        scenario_label = ttk.Label(self.frame, text="Configuration : " + self.get_scenario(globals.global_new_id_observation), padding=10,
                                   anchor="w", font=globals.global_font_title1)
        scenario_label.pack(fill=tk.BOTH)
        session_label = ttk.Label(self.frame, text="Session : " + self.get_session(globals.global_new_id_observation),
                                  padding=10, anchor="w", font=globals.global_font_title1)
        session_label.pack(fill=tk.BOTH)
        participant_label = ttk.Label(self.frame, text="Particpant : " +
                                                       self.get_participant(globals.global_new_id_observation),
                                      padding=10, anchor="w", font=globals.global_font_title1)
        participant_label.pack(fill=tk.BOTH)

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
                  padding=5, anchor="center", font=globals.global_font_text).pack(side=tk.LEFT)
        ttk.Label(frame_title, background="lightgrey", width=20, text="Label", borderwidth=1, relief="solid",
                  padding=5, anchor="center", font=globals.global_font_text).pack(side=tk.LEFT)
        ttk.Label(frame_title, background="lightgrey", width=80, text="Description", borderwidth=1, relief="solid",
                  padding=5, anchor="center", font=globals.global_font_text).pack(side=tk.LEFT)
        ttk.Label(frame_title, background="lightgrey", width=20, text="State", borderwidth=1, relief="solid",
                  padding=5, anchor="center", font=globals.global_font_text).pack(side=tk.LEFT)

        self.data_frame = ttk.Frame(self.frame_canvas)
        self.data_frame.pack(pady=5, fill=tk.BOTH, expand=tk.TRUE)

        self.program_pid = None

        self.sensor_type_frame_list = []

    def show_page(self):
        """!
        @brief The show_page function creates and displays all the elements of the "summary" page
        @param self : the instance
        @param is_observation : True if the page is to be displayed in the context of an observation
        @return Nothing
        """


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
                # Retrieve information from sensors of this type from the database
                sensor_infos = self.get_sensor_infos_for_type(sensor_type_id)
                if sensor_infos:
                    sensor_type_button = ttk.Button(
                        self.button_frame,
                        text=sensor_type,
                        command=lambda type=sensor_type: self.display_sensor_info(type),
                        padding=5
                    )
                    sensor_type_button.pack(side=tk.LEFT)

                self.create_sensor_info(sensor_infos, sensor_type)

            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            print(f"Error: {err}")

    def create_sensor_info(self, sensor_infos, sensor_type):

        for sensor_info in sensor_infos:
            sensor_frame = ttk.Frame(self.data_frame)

            self.sensor_type_frame_list.append({
                "type": sensor_type,
                "frame": sensor_frame
            })
            #sensor_frame.pack(pady=5, fill=tk.BOTH, expand=tk.TRUE)

            sensor_label = sensor_info[0]
            sensor_description = sensor_info[1]

            # Showing the type of the sensor
            ttk.Label(sensor_frame, text=f"{sensor_type}", width=20, anchor='w', wraplength=140,
                      background="white", borderwidth=1, relief="solid", padding=5, font=globals.global_font_text).pack(side=tk.LEFT)

            # Creating a text widget tht will contain the label associated with the sensor
            ttk.Label(sensor_frame, text=f"{sensor_label}", borderwidth=1, background="white", width=20,
                      relief="solid", padding=5, font=globals.global_font_text).pack(side=tk.LEFT)

            # Showing the description of the sensor
            ttk.Label(sensor_frame, text=f"{sensor_description}", borderwidth=1, background="white", width=80,
                      relief="solid", padding=5, font=globals.global_font_text).pack(side=tk.LEFT)

            # Showing the current state of the sensor
            label_state = ttk.Label(sensor_frame, text=f"Etat en direct", borderwidth=1, background="white", width=20,
                      relief="solid", padding=5, anchor="center", font=globals.global_font_text)

            match sensor_type:
                case "Button":
                    label_state.configure(text="Action : Unknown")
                case "Door":
                    label_state.configure(text="Contact : Unknown")
                case "Motion":
                    label_state.configure(text="Occupancy : Unknown")
                case "Vibration":
                    label_state.configure(text="Vibration : Unknown")

            label_state.pack(side=tk.LEFT)

            globals.thread_done = False

            sensor_friendly_name = sensor_type + "/" + sensor_label

            my_thread = threading.Thread(target=model.local_mqtt.get_sensor_value,
                                         args=(sensor_friendly_name, label_state))
            my_thread.start()

    def display_sensor_info(self, sensor_type):
        """!
        @brief Displays information about all sensors of a selected type.
        @param self: Instance reference.
        @param sensor_infos: all the sensors associated with a type of sensor.
        @param sensor_type: Type of sensor.
        @return None
        """
        for sensor_type_frame in self.sensor_type_frame_list:
            if sensor_type_frame["type"] != sensor_type:
                sensor_type_frame["frame"].pack_forget()
            else:
                sensor_type_frame["frame"].pack(pady=5, fill=tk.BOTH, expand=tk.TRUE)

        """globals.thread_done = True
        #self.data_frame.destroy()

        for sensor_info in sensor_infos:
            sensor_frame = ttk.Frame(self.data_frame)
            sensor_frame.pack(pady=5, fill=tk.BOTH, expand=tk.TRUE)

            sensor_label = sensor_info[0]
            sensor_description = sensor_info[1]

            # Showing the type of the sensor
            ttk.Label(sensor_frame, text=f"{sensor_type}", width=20, anchor='w', wraplength=140,
                      background="white", borderwidth=1, relief="solid", padding=5, font=globals.global_font_text).pack(side=tk.LEFT)

            # Creating a text widget tht will contain the label associated with the sensor
            ttk.Label(sensor_frame, text=f"{sensor_label}", borderwidth=1, background="white", width=20,
                      relief="solid", padding=5, font=globals.global_font_text).pack(side=tk.LEFT)

            # Showing the description of the sensor
            ttk.Label(sensor_frame, text=f"{sensor_description}", borderwidth=1, background="white", width=80,
                      relief="solid", padding=5, font=globals.global_font_text).pack(side=tk.LEFT)

            # Showing the current state of the sensor
            label_state = ttk.Label(sensor_frame, text=f"Etat en direct", borderwidth=1, background="white", width=20,
                      relief="solid", padding=5, anchor="center", font=globals.global_font_text)

        """
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

    def start_observation(self):
        #TODO voir avec les indus comment recuperer et inserer les datas

        arguments = []

        sensor_list = local.get_sensors_from_observation(globals.global_new_id_observation)
        print("\033[95msensor list: ", sensor_list, "\033[0m")
        for sensor in sensor_list:
            arguments.append(sensor["type"] + "/" + sensor["label"])

        print("arguments : ", arguments)
        command = ["python", "/home/prisme/Prisme@home/PRISMATHOME/reception.py"] + arguments

        # Start the main program
        main_program = subprocess.Popen(command)

        self.program_pid = main_program.pid

        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Q3fhllj2",
                database="prisme_home_1"
            )
            cursor = conn.cursor()

            # Execute a request
            query_update = "UPDATE prisme_home_1.observation SET active=1 WHERE id_observation=%s"
            cursor.execute(query_update, (globals.global_new_id_observation,))  # Pass label as a tuple
            conn.commit()

        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            return None

        finally:
            # Closing the cursor and connection
            cursor.close()
            conn.close()


    def stop_observation(self):
        # TODO Mathilde : voir où appeller la fonction car lorsque que je la met au bonne endroit ca
        #  pose probleme
        #  + voir avec les indus comment stopper la reception des datas
        os.kill(self.program_pid, signal.SIGTERM)
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
