import tkinter as tk
from tkinter import ttk
from tkinter import *
import globals
import mysql

# TODO remplacer cette liste par une requête listant les différents types de capteurs stockés dans la BDD
sensor_types_id = ["presence", "pressure", "opening", "button"]


class Summary:
    def __init__(self, master):
        self.master = master
        self.frame = ttk.Frame(self.master)

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
        scenario_label = ttk.Label(scenario_frame, text="Scenario : " + self.get_scenario_label(), padding=10)
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

        button_frame = ttk.Frame(self.frame)
        button_frame.pack(padx=5)

        self.sensor_text = tk.Text(self.frame)
        self.sensor_text.pack(fill=tk.BOTH, expand=tk.TRUE)

        for sensor_type in sensor_types_id:
            sensor_type_button = ttk.Button(button_frame, text=self.get_sensor_label(sensor_type), command=lambda st=sensor_type : self.display_sensor_info(st), padding=5)
            sensor_type_button.pack(fill=tk.BOTH, side=tk.LEFT)

    def display_sensor_info(self, sensor_type):

        self.sensor_text.configure(state='normal')

        self.sensor_text.delete("1.0", tk.END)

        for sensor_id in self.get_sensors_id_from_type(sensor_type):
            # TODO remplacer le text du label par les infos des capteurs du type de sensor_type
            self.sensor_text.insert(0.1, sensor_type + " sensor" + sensor_id + " : \n" +
                                    "\tLabel : " + self.get_sensor_label(sensor_id) + "\n" +
                                    "\tDescription : " + self.get_sensor_description(sensor_id) + "\n" +
                                    "\tStatus : " + self.get_sensor_status(sensor_id) + "\n\n")
        self.sensor_text.configure(state='disabled')


    def clear_page(self):
        self.frame.destroy()


    def get_scenario_label(self):
        # TODO Modifier la fonction pour qu'elle retourne le scénario de la configuration en cours
        return "Ceci est le scénario de l'observation"

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
        return "Label du capteur " + id_sensor

    def get_sensor_description(self, id_sensor):
        # TODO Modifier la fonction pour qu'elle retourne la description d'un capteur en fonction de son id
        return "Description du capteur " + id_sensor

    def get_sensor_status(self, id_sensor):
        # TODO Modifier la fonction pour qu'elle retourne le status d'un capteur en fonction de son id
        return "Status du capteur " + id_sensor

