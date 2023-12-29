import tkinter as tk
from tkinter import ttk
import mysql.connector
import globals

class LabelisationSensor:
    def __init__(self, master):
        self.master = master
        self.frame = ttk.Frame(self.master)
        self.sensor_entries = []  # List to hold the label, description entries for each sensor, and sensor type ID

    def show_page(self):
        self.frame = ttk.Frame(self.master)
        self.frame.pack(expand=True)

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


    def create_labeled_entry(self, label_text, sensor_type_id):
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

        # Append the sensor_type_id to the sensor_entries list along with label and description
        self.sensor_entries.append((sensor_type_id, entry_label, entry_description))

    def print_sensor_data(self):
        # Iterate through the sensor_entries list and print the label and description for each sensor
        for sensor_type_id, label_entry, description_entry in self.sensor_entries:
            label = label_entry.get()
            description = description_entry.get()
            print(f"Sensor Type ID: {sensor_type_id}, Label - {label}, Description - {description}")

            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="prismathome"
            )
            cursor = conn.cursor()

            # Execute the INSERT query using the actual sensor_type_id
            query = "INSERT INTO sensor_config (id_config, id_sensor_type, sensor_label, sensor_description) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (globals.global_id_config, sensor_type_id, label, description))
            conn.commit()
            cursor.close()
            conn.close()

    def clear_page(self):
        self.frame.destroy()