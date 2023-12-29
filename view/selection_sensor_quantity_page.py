import tkinter as tk
from tkinter import ttk
from tkinter import *
import globals
import mysql.connector

class QuantitySensor:
    def __init__(self, master):
        self.master = master
        self.frame = ttk.Frame(self.master)

    def fetch_sensor_types(self):

        # Connexion à la base de données MySQL
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="prismathome"
        )
        cursor = conn.cursor()

        # Exécutez une requête
        cursor.execute("SELECT id_type, type FROM sensor_type")  # Adaptez cette requête à votre BDD
        return cursor.fetchall()
    def show_page(self):

        # Create a main frame which will be centered in the window
        self.frame = ttk.Frame(self.master)
        self.frame.pack(expand=True)

        # Create a frame for the sensor selectors inside the main frame
        self.frame_sensors = tk.Frame(self.frame, padx=10, pady=10)
        self.frame_sensors.pack()

        # Récupérez les types de capteurs de la BDD
        sensor_types = self.fetch_sensor_types()

        # Créez dynamiquement des listes déroulantes pour chaque type de capteur
        self.sensor_vars = {}  # Dictionnaire pour stocker les StringVars
        for id, type in sensor_types:
            sensor_frame = tk.LabelFrame(self.frame_sensors, text=type, padx=5, pady=5)
            sensor_var = tk.StringVar()
            combobox = ttk.Combobox(sensor_frame, values=[0, 1, 2, 3, 4, 5], state="readonly", width=5, textvariable=sensor_var)
            combobox.set(0)  # Valeur par défaut
            combobox.pack(padx=10, pady=5)
            sensor_frame.pack(side=tk.LEFT, padx=10)
            self.sensor_vars[id] = sensor_var  # Stockez la variable pour une utilisation ultérieure

    def clear_page(self):
        self.frame.destroy()
        self.frame_sensors.destroy()

    def on_next_button_click(self):
        globals.sensor_counts.clear()

        # Récupérez les valeurs des StringVars et les stockez dans le dictionnaire sensor_counts de globals
        for sensor_type, sensor_var in self.sensor_vars.items():
            globals.sensor_counts[sensor_type] = int(sensor_var.get())

        # Imprimez les valeurs pour vérifier
        for sensor_type, count in globals.sensor_counts.items():
            print(f"Number of id_type {sensor_type} Sensors selected:", count)