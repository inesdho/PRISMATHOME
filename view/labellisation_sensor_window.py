import tkinter as tk
from tkinter import ttk
import globals


# TODO remplacer cette liste par une requête listant les différents capteurs de la configuration en cours
#sensor_labels = ['Presence sensor 1', 'Presence sensor 2', 'Opening sensor 1', 'Pressure sensor 1']


class LabelisationSensor:
    def __init__(self, master):
        self.master = master
        self.frame = ttk.Frame(self.master)

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

    def clear_page(self):
        self.frame.destroy()
