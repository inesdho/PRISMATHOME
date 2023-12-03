import tkinter as tk
from tkinter import ttk


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
        label.pack(pady=10)

        # Configuration list
        options = ["Option 1", "Option 2", "Option 3"]
        configuration_label = ttk.Label(self.frame, text="Configuration")
        configuration_label.pack(pady=10)
        self.configuration_combobox = ttk.Combobox(self.frame, values=options)
        self.configuration_combobox.pack(pady=10)

        # Session input
        session_label = ttk.Label(self.frame, text="Session")
        session_label.pack()
        self.session_entry = ttk.Entry(self.frame)
        self.session_entry.pack(pady=10)

        # Participant input
        participant_label = ttk.Label(self.frame, text="Participant")
        participant_label.pack()
        self.participant_entry = ttk.Entry(self.frame)
        self.participant_entry.pack(pady=10)

        # Validation button
        button = ttk.Button(self.frame, text="Import configuration", command=self.on_button_click)
        button.pack(pady=20)

    def clear_page(self):
        self.frame.destroy()

    # Get the data from the user input
    def on_button_click(self):
        configuration_value = self.configuration_combobox.get()
        session_value = self.session_entry.get()
        participant_value = self.participant_entry.get()

        # Print the chosen data
        print("Configuration :", configuration_value)
        print("Session :", session_value)
        print("Participant :", participant_value)
