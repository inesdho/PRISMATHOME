"""!
@file new_observation_page.py
@brief This file will contain all the widgets and functions related to the "new observation" page itself
@author Naviis-Brain
@version 1.0
@date
"""

import tkinter as tk
from tkinter import ttk
import globals
from model import local
import getpass

import mysql
from controller.entry_manager import EntryManager


class NewObservation:
    def __init__(self, master):
        """!
        @brief The __init__ function sets the master frame in parameters as the frame that will contain all the widgets of
        this page
        @param self : the instance
        @param master : the master frame (created in the controller.py file)
        @return Nothing
        """
        self.master = master
        self.frame = ttk.Frame(self.master)
        self.configuration_combobox = ttk.Combobox(self.frame)
        self.configuration_values = []

        # Main frame of the new observation window
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Label "New Observation"
        label = ttk.Label(self.frame, text="New Observation", font=globals.global_font_title)
        label.pack(pady=20)


    def show_page(self):
        """!
        @brief The show_page function creates and displays all the elements of the "new_observation" page
        @param self : the instance
        @return Nothing
        """

        # User input
        user_label = ttk.Label(self.frame, text="User", font=globals.global_font_title1)
        user_label.pack()
        user_label = ttk.Label(self.frame, text=getpass.getuser(), font=18)
        user_label.pack(pady=10)
        # TODO paul I guess ? remplacer le default texte par la valeur que tu as crée de l'utilisateur de la session
        #self.user_entry = EntryManager(self.frame, min=1, max=30, has_width=30, default_text="User")

        """list_configuration_labels = [config['label'] for config in configurations]
        list_configuration_ids = [config['id_config'] for config in configurations]"""

        # Configuration list
        configuration_label = ttk.Label(self.frame, text="Configuration", font=globals.global_font_title1)
        configuration_label.pack()

        # Get the configuration labels and ids
        configurations = local.get_config_labels_ids()

        if configurations is not None:
            # Creation of a tuple list
            self.configuration_values = [(config['label'], config['id_config']) for config in configurations]

            # Creation of a combobox with the list of configuration labels
            self.configuration_combobox = ttk.Combobox(self.frame, width=29)
            self.configuration_combobox['values'] = [label for label, id_config in self.configuration_values]
            self.configuration_combobox.set(self.configuration_values[0][0])
            self.configuration_combobox.pack(pady=10)
        else:
            configurations = ['No configuration available']
            self.configuration_combobox = ttk.Combobox(self.frame, values=configurations, width=29)
            self.configuration_combobox.set(configurations[0])
            self.configuration_combobox.pack(pady=10)

        # Session input
        session_label = ttk.Label(self.frame, text="Session", font=globals.global_font_title1)
        session_label.pack()
        self.session_entry = EntryManager(self.frame, min=1, max=100, has_width=30, default_text="Session")

        # Participant input
        participant_label = ttk.Label(self.frame, text="Participant", font=globals.global_font_title1)
        participant_label.pack()
        self.participant_entry = EntryManager(self.frame, min=1, max=70, has_width=30, default_text="Participant")

    def clear_page(self):
        """!
        @brief This functions clears the entire "new observation" page
        @param self : the instance
        @return Nothing
        """
        self.frame.destroy()

    def on_import_button_click(self):
        """!
        @brief This functions collects all the datas entered by the user
        @param self : the instance
        @return Nothing
        """
        # Get the new id_config from function
        id_config = self.get_selected_id_config()
        # Get participant from entry
        participant = self.participant_entry.get()
        # Get new id session from function
        id_session = local.get_new_id_session(participant, id_config)
        # Get session label from entry
        session_label = self.session_entry.get()

        globals.global_participant_selected = participant
        globals.global_id_system_selected = local.get_system_id()
        globals.global_id_config_selected = id_config
        globals.global_id_session_selected = id_session
        globals.global_session_label_selected = session_label

        # Caching
        globals.global_id_config_selected = id_config


    def get_selected_id_config(self):
        """
           @brief Retrieves the 'id_config' associated with the selected label in the combobox.

           @return The 'id_config' associated with the selected label in the combobox.
                   Returns None if no item is selected or if the selected item is not found.
           """
        selected_label = self.configuration_combobox.get()
        for label, id_config in self.configuration_values:
            if label == selected_label:
                return id_config
        return None
