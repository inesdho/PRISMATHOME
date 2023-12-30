import tkinter as tk
from tkinter import ttk
from controller.input_manager import Input


class NewObservation:
    def __init__(self, master):
        self.master = master
        self.frame = ttk.Frame(self.master)

    def show_page(self):
        # Main frame of the new observation window
        self.frame = ttk.Frame(self.master)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Label "New Observation"
        label = ttk.Label(self.frame, text="New Observation", font=16)
        label.pack(pady=20)

        # User input
        user_label = ttk.Label(self.frame, text="User")
        user_label.pack()
        # TODO paul I guess ? remplacer le default texte par la valeur que tu as crée de l'utilisateur de la session
        self.user_entry = Input(self.frame, min=1, max=30, has_width=30, default_text="User")


        # Configuration list
        # TODO réccupérer les noms des configurations
        options = ["Option 1", "Option 2", "Option 3"]
        configuration_label = ttk.Label(self.frame, text="Configuration")
        configuration_label.pack()
        self.configuration_combobox = ttk.Combobox(self.frame, values=options, width=29)
        self.configuration_combobox.insert(-1, options[0])
        self.configuration_combobox.pack(pady=10)

        # Observation label input
        observation_label_label = ttk.Label(self.frame, text="Observation label")
        observation_label_label.pack()
        self.observation_label_entry = Input(self.frame, min=1, max=80, has_width=30, default_text="Label")

        # Observation description input
        observation_description_label = ttk.Label(self.frame, text="Observation description")
        observation_description_label.pack()
        self.observation_description_entry = Input(self.frame, min=1, max=200, has_width=100, default_text="Description")

        # Session input
        session_label = ttk.Label(self.frame, text="Session")
        session_label.pack()
        self.session_entry = Input(self.frame, min=1, max=100, has_width=100, default_text="Session")

        # Participant input
        participant_label = ttk.Label(self.frame, text="Participant")
        participant_label.pack()
        self.participant_entry = Input(self.frame, min=1, max=70, has_width=70, default_text="Participant")

    def clear_page(self):
        self.frame.destroy()

    # Get the data from the user input
    def on_button_click(self):

        # Print the chosen data
        print("User :", self.user_entry.get())
        print("Configuration :", self.configuration_combobox.get())
        print("Observation label :", self.observation_label_entry.get())
        print("Observation description :", self.observation_description_entry.get())
        print("Session :", self.session_entry.get())
        print("Participant :", self.participant_entry.get())
