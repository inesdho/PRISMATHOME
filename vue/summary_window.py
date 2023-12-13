import tkinter as tk
from tkinter import ttk

# TODO remplacer cette liste par une requête listant les différents types de capteurs stockés dans la BDD
sensor_types = ["presence", "pressure", "opening"]

class Summary:
    def __init__(self, master):
        self.master = master
        self.frame = ttk.Frame(self.master)

        # Will contain the expanding frames
        self.expanding_frames = {}

    def show_page(self):
        self.frame_text = ttk.Frame(self.master, padding="10px")
        self.frame_text.pack(fill=tk.BOTH, expand=True)

        label = ttk.Label(self.frame_text, text="Summary", anchor='n', font='16')
        label.pack(fill='both', expand=True)

        # Label wich contain the information relative to the current observation
        label_observation_info = ttk.Label(self.frame_text, text="Scenario : " + self.get_scenario_label() + "\n" +
                                                                 "Session : " + self.get_session() + "\n" +
                                                                 "Participant : " + self.get_participant() + "\n\n" )
        label_observation_info.pack(side='left', pady=5)

        self.frame_sensor_type  = ttk.Frame(self.master, padding="10px")
        self.frame_sensor_type.pack(fill=tk.BOTH, expand=True)



        # Show a button that will display the details of a type of sensor
        self.show_sensor_types()

    def show_sensor_types(self):

        for sensor_type in sensor_types:
            if self.exist_in_this_config(sensor_type):
                # Sensors type
                sensor_frame = ttk.Frame(self.frame_sensor_type)
                sensor_frame.pack(pady=5, fill=tk.BOTH)

                toggle_button = ttk.Button(sensor_frame, text=sensor_type, command=lambda st=sensor_type: self.toggle_frame(st))
                toggle_button.pack(pady=5)

                self.create_expanding_frame(sensor_type, sensor_frame)



    def toggle_frame(self, sensor_type):
        # Get the actual frame
        frame = self.expanding_frames.get(sensor_type)

        # Show or hide the frame depending on the current state
        if frame.winfo_ismapped():
            frame.pack_forget()
        else:
            frame.pack(fill=tk.BOTH, expand=True)

    def create_expanding_frame(self, sensor_type, sensor_frame):
        # Create a frame
        expanding_frame = ttk.Frame(sensor_frame, relief="sunken")
        expanding_frame.pack(fill=tk.BOTH, expand=True)

        # Add content to the frame
        text_sensor = tk.Text(expanding_frame)
        text_sensor.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(text_sensor, command=text_sensor.yview())
        scrollbar.pack(side="right", fill="y")

        # Configure the Text widget to use the scrollbar
        text_sensor.config(yscrollcommand=scrollbar.set)

        for sensor_id in self.get_sensors_id_from_type(sensor_type):
            # TODO remplacer le text du label par les infos des capteurs du type de sensor_type
            text_sensor.insert(1.0, sensor_type + " sensor" + sensor_id + " : \n" +
                               "\tLabel : " + self.get_sensor_label(sensor_id) + "\n" +
                               "\tDescription : " + self.get_sensor_description(sensor_id) + "\n" +
                               "\tStatus : " + self.get_sensor_status(sensor_id) + "\n\n")

        # Hide the frame when the page is loaded
        expanding_frame.pack_forget()

        # Add the frame to the dictionaries
        self.expanding_frames[sensor_type] = expanding_frame


    def get_scenario_label(self):
        # TODO Modifier la fonction pour qu'elle retourne le scénario de l'observation en cours
        return "Ceci est le scénario de l'observation"

    def get_session(self):
        # TODO Modifier la fonction pour qu'elle retourne la session de l'observation en cours
        return "Ceci est la session de l'observation"

    def get_participant(self):
        # TODO Modifier la fonction pour qu'elle retourne le particpant de l'observation en cours
        return "Ceci est le participant de l'observation"

    def exist_in_this_config(self, sensor_type):
        # TODO Modifier la fonction pour qu'elle retourne true si ce type de capteur est présent dans la configuration en cours sinon false
        return True

    def get_sensors_id_from_type(self,sensor_type):
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


