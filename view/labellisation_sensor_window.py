import tkinter as tk
from tkinter import ttk

import mysql

import globals

class LabelisationSensor:
    def __init__(self, master):
        self.master = master
        self.frame = ttk.Frame(self.master)
        self.sensor_entries = []  # List to hold the label and description entries for each sensor


    def show_page(self):
        sensor_labels = []
        for i in range(int(globals.num_presence_sensors)):
            sensor_labels.append(f'Presence sensor {i+1}')
        for i in range(int(globals.num_opening_sensors)):
            sensor_labels.append(f'Opening sensor {i+1}')
        for i in range(int(globals.num_pressure_sensors)):
            sensor_labels.append(f'Pressure sensor {i+1}')

        self.frame = ttk.Frame(self.master)
        self.frame.pack(expand=True)

        # Create entries for sensors
        for label in sensor_labels:
            self.create_labeled_entry(label)

        next_button = ttk.Button(self.frame, text='Next', command=self.print_sensor_data)
        next_button.pack()

    # Helper function to create a labeled entry with two text boxes, one for label and one for description
    def create_labeled_entry(self, label_text):
        entry_frame = ttk.Frame(self.frame)
        entry_frame.pack(fill=tk.X, pady=5)
        label = ttk.Label(entry_frame, text=label_text, width=20, anchor='w')
        label.pack(side=tk.LEFT)

        label_label = ttk.Label(entry_frame, text="Label :", width=10)
        label_label.pack(side=tk.LEFT)
        entry_label = ttk.Entry(entry_frame, width=20)
        entry_label.pack(side=tk.LEFT, padx=5)

        description_label = ttk.Label(entry_frame, text="Description :", width=10)
        description_label.pack(side=tk.LEFT)
        entry_description = ttk.Entry(entry_frame, width=50)
        entry_description.pack(side=tk.LEFT, padx=5)

        self.sensor_entries.append((label_text, entry_label, entry_description))

    def print_sensor_data(self):
        # Iterate through the sensor_entries list and print the label and description for each sensor
        for sensor_id, label_entry, description_entry in self.sensor_entries:
            label = label_entry.get()
            description = description_entry.get()
            print(f"{sensor_id}: Label - {label}, Description - {description}")

        for sensor_id in self.sensor_entries:
            print(f"{sensor_id}")


        # Connexion à la base de données MySQL
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="prismathome"
        )
        cursor = conn.cursor()

        # Exécutez une requête
        query = "INSERT INTO sensor_config (id_config, id_sensor_type, label, description)VALUES(%s, %s, %s, %s)"
        cursor.execute(query, (id_config, id_user, scenarioname, description))
        conn.commit()

    def clear_page(self):
        self.frame.destroy()
