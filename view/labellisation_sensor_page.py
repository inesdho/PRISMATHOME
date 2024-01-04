"""!
@file labellisation_sensor_page.py
@brief This file will contain all the widgets and functions related to the "labellisation sensor" page itself
@author Naviis-Brain
@version 1.0
@date
"""
import tkinter as tk
from tkinter import ttk
import mysql.connector
import globals
from controller.entry_manager import EntryManager

class LabelisationSensor:
    """!
    @brief The __init__ function sets the master frame in parameters as the frame that will contain all the widgets of
    this page
    @param the instance, the master frame (created in the controller.py file)
    @return Nothing
    """
    def __init__(self, master):
        self.master = master
        self.sensor_entries = []  # List to hold the label, description entries for each sensor, and sensor type ID

        self.frame = ttk.Frame(self.master)
        self.frame.pack(fill=tk.BOTH, expand=tk.TRUE)

        # Displays the title of the page
        label = ttk.Label(self.frame, text="Sensor labellisation", font=16)
        label.pack(pady=20)

        # Creation of a canvas in order to add a scrollbar in case to many lines of sensors are displayed
        self.canvas = tk.Canvas(self.frame)
        self.scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill="y")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.frame_canvas = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), anchor='nw', window=self.frame_canvas)

    """!
    @brief The show_page function creates and displays all the elements of the "labellisation sensor" page
    @param the instance
    @return Nothing
    """
    def show_page(self):

        # Create entries for the sensors using the data from globals.sensor_counts
        for sensor_type_id, quantity in globals.sensor_counts.items():
            for i in range(quantity):
                try:
                    conn = mysql.connector.connect(
                        host="localhost",
                        user="root",
                        password="",
                        database="prismathome"
                    )
                    cursor = conn.cursor()
                    query = "SELECT type FROM sensor_type WHERE id_type = %s"
                    cursor.execute(query, (sensor_type_id,))
                    type_result = cursor.fetchone()
                    cursor.close()
                    conn.close()

                    if type_result:
                        sensor_type = type_result[0]
                        label_text = f'{sensor_type} sensor {i+1}'
                    else:
                        label_text = 'Unknown sensor'
                        sensor_type_id = None

                    # Pass the sensor_type_id to the create_labeled_entry method
                    self.create_labeled_entry(label_text, sensor_type_id)
                except mysql.connector.Error as err:
                    print(f"Error: {err}")
                    label_text = 'Error sensor'
                    sensor_type_id = None
                    self.create_labeled_entry(label_text, sensor_type_id)

        # Configurer la barre de défilement pour suivre la hauteur du contenu
        self.frame_canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    """!
    @brief This function creates label entries according to the sensor quantity of each type selected by the user in the
    selection sensor quantity page. The user can then enter the label and description to attribute to each sensor
    @param the instance, label_text -> the label of the sensor, sensor_type_id
    @return Nothing
    """
    def create_labeled_entry(self, label_text, sensor_type_id):
        entry_frame = ttk.Frame(self.frame_canvas)
        entry_frame.pack(fill=tk.X, pady=5)
        label = ttk.Label(entry_frame, text=label_text, width=20, anchor='w')
        label.pack(side=tk.LEFT)

        label_label = ttk.Label(entry_frame, text="Label :", width=10)
        label_label.pack(side=tk.LEFT)
        entry_label = EntryManager(entry_frame, min=1, max=80, has_width=20, auto_pack=False, default_text="Label")
        entry_label.get_entry().pack(side=tk.LEFT, padx=5)

        description_label = ttk.Label(entry_frame, text="Description :", width=10)
        description_label.pack(side=tk.LEFT)
        entry_description = EntryManager(entry_frame, min=1, max=600, has_width=50, has_special_char=True, auto_pack=False,
                                         default_text="Description")
        entry_description.get_entry().pack(side=tk.LEFT, padx=5)

        # Append the sensor_type_id to the sensor_entries list along with label and description
        self.sensor_entries.append((sensor_type_id, entry_label, entry_description))

    """!
    @brief This function saves the label and description entered by the user for each sensor into global variables 
    @param the instance
    @return Nothing
    """
    def get_sensor_data(self):

        globals.global_sensor_entries.clear()
        # Iterate through the sensor_entries list and print the label and description for each sensor
        for sensor_type_id, label_entry, description_entry in self.sensor_entries:
            label = label_entry.get()
            description = description_entry.get()
            globals.global_sensor_entries.append((sensor_type_id, label, description))
            print(f"Sensor Type ID: {sensor_type_id}, Label - {label}, Description - {description}")

    """!
    @brief This functions clears the entire "new observation" page
    @param the instance
    @return Nothing
    """
    def clear_page(self):
        self.canvas.destroy()
