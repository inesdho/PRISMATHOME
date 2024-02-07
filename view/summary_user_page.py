"""!
@file summary_admin_page.py
@brief This file will contain all the widgets and functions related to the "summary" page itself
@author Naviis-Brain
@version 1.0
@date 31st January 2024
"""
import tkinter as tk
from tkinter import ttk
from utils import globals
from model import local
import threading
import mqtt.local_mqtt


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

        # Displays the title of the page
        label = ttk.Label(self.frame, text="SUMMARY USER", font=globals.global_font_title, foreground='#3daee9')
        label.pack(pady=30)

        self.observation_state = ttk.Label(self.frame, text=" ", font=globals.global_font_title1)
        self.observation_state.pack(pady=10)

        # Information about the configuration
        scenario_label = ttk.Label(self.frame,
                                   text="Configuration : "
                                        + local.get_config_label_from_observation_id(globals.global_new_id_observation),
                                   padding=10,
                                   anchor="w", font=globals.global_font_title1)
        scenario_label.pack(fill=tk.BOTH)
        session_label = ttk.Label(self.frame, text="Session : " + local.get_observation_info(
            globals.global_new_id_observation, 'session_label'),
                                  padding=10, anchor="w", font=globals.global_font_title1)
        session_label.pack(fill=tk.BOTH)
        participant_label = ttk.Label(self.frame, text="Particpant : " +
                                                       local.get_observation_info(globals.global_new_id_observation, 'participant'),
                                      padding=10, anchor="w", font=globals.global_font_title1)
        participant_label.pack(fill=tk.BOTH)

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
        ttk.Label(frame_title, background="#3daee9", width=20, text="State", borderwidth=0.5, relief="solid",
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
            all_sensor_types = local.get_sensor_type_list()

            # Creation of the button to display all the sensor
            all_ssensor_type_button = ttk.Button(
                self.button_frame,
                text="All sensor",
                command=lambda type=-1: self.display_sensor_info(type),
                padding=5
            )
            all_ssensor_type_button.pack(side=tk.LEFT, padx=5)

            for sensor_type_id, sensor_type in all_sensor_types:
                # Retrieve information from sensors of this type from the database
                sensor_infos = local.get_sensor_info_from_observation(globals.global_new_id_observation, sensor_type_id)

                if sensor_infos:
                    if sensor_infos:
                        sensor_type_button = ttk.Button(
                            self.button_frame,
                            text=sensor_type,
                            command=lambda type=sensor_type: self.display_sensor_info(type),
                            padding=5
                        )
                        sensor_type_button.pack(side=tk.LEFT, padx=5)
                    self.create_sensor_info(sensor_infos, sensor_type)

        except Exception as err:
            print(f"Error: {err}")

    def create_sensor_info(self, sensor_infos, sensor_type):
        for sensor_info in sensor_infos:
            sensor_frame = ttk.Frame(self.data_frame)

            self.sensor_type_frame_list.append({
                "type": sensor_type,
                "frame": sensor_frame
            })

            #sensor_frame.pack(pady=5, fill=tk.BOTH, expand=tk.TRUE)

            # Showing the type of the sensor
            ttk.Label(sensor_frame, text=f"{sensor_type}", width=20, anchor='w', wraplength=140,
                      background="white", borderwidth=0.5, relief="solid", padding=5, font=globals.global_font_text).pack(side=tk.LEFT)


            # Creating a text widget tht will contain the label associated with the sensor
            ttk.Label(sensor_frame, text=f"{sensor_info['label']}", borderwidth=0.5, background="white", width=20,
                      relief="solid", padding=5, font=globals.global_font_text).pack(side=tk.LEFT)

            # Showing the description of the sensor
            ttk.Label(sensor_frame, text=f"{sensor_info['description']}", borderwidth=0.5, background="white", width=80,
                      relief="solid", padding=5, font=globals.global_font_text).pack(side=tk.LEFT)

            # Showing the current state of the sensor
            label_state = ttk.Label(sensor_frame, text=f"Etat en direct", borderwidth=0.5, background="white", width=20,
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

            sensor_friendly_name = sensor_type + "/" + sensor_info['label']
            my_thread = threading.Thread(target=mqtt.local_mqtt.get_sensor_value,
                                         args=(sensor_friendly_name, label_state))
            my_thread.start()

    def display_sensor_info(self, sensor_type):
        """!
        @brief Displays information about all sensors of a selected type, or all the sensor if sensor_type == -1
        @param self: Instance reference.
        @param sensor_type: Type of sensor.
        @return None
        """
        # The value -1 is used to display all the sensor at once regarding of their type
        if sensor_type ==-1:
            for sensor_type_frame in self.sensor_type_frame_list:
                sensor_type_frame["frame"].pack(pady=5, fill=tk.BOTH, expand=tk.TRUE)
        # If the value is not -1 only the sensor with the type that match are displayed
        else:
            for sensor_type_frame in self.sensor_type_frame_list:
                if sensor_type_frame["type"] != sensor_type:
                    sensor_type_frame["frame"].pack_forget()
                else:
                    sensor_type_frame["frame"].pack(pady=5, fill=tk.BOTH, expand=tk.TRUE)

        # Configure the scroll region to follow the content of the frame
        self.frame_canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def clear_page(self):
        """!
        @brief This functions clears the entire "summary user" page
        @param self : the instance
        @return Nothing
        """
        self.data_frame.destroy()
        self.frame_canvas.destroy()
        self.canvas.destroy()
        self.frame.destroy()
        self.button_frame.destroy()

    def clear_sensor_entries(self):
        """!
        @brief This function clears the sensor entries after validation.
        """
        globals.global_sensor_entries.clear()
        for _, label_entry, description_entry in globals.global_sensor_entries:
            label_entry.set('')
            description_entry.set('')