"""!
@file new_observation_page.py
@brief This file will contain all the widgets and functions related to the "new observation" page itself
@author Naviis-Brain
@version 1.0
@date
"""

import tkinter as tk
from tkinter import ttk

import mysql

from controller.entry_manager import EntryManager


class NewObservation:
    """!
    @brief The __init__ function sets the master frame in parameters as the frame that will contain all the widgets of
    this page
    @param the instance, the master frame (created in the controller.py file)
    @return Nothing
    """
    def __init__(self, master):
        self.master = master
        self.frame = ttk.Frame(self.master)

    """!
    @brief The show_page function creates and displays all the elements of the "new_observation" page
    @param the instance
    @return Nothing
    """
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
        self.user_entry = EntryManager(self.frame, min=1, max=30, has_width=30, default_text="User")


        # Configuration list
        options = self.get_config()
        configuration_label = ttk.Label(self.frame, text="Configuration")
        configuration_label.pack()
        self.configuration_combobox = ttk.Combobox(self.frame, values=options, width=29)
        self.configuration_combobox.pack(pady=10)

        # Session input
        session_label = ttk.Label(self.frame, text="Session")
        session_label.pack()
        self.session_entry = EntryManager(self.frame, min=1, max=100, has_width=100, default_text="Session")

        # Participant input
        participant_label = ttk.Label(self.frame, text="Participant")
        participant_label.pack()
        self.participant_entry = EntryManager(self.frame, min=1, max=70, has_width=70, default_text="Participant")

    """!
    @brief This functions clears the entire "new observation" page
    @param the instance
    @return Nothing
    """
    def clear_page(self):
        self.frame.destroy()

    """!
    @brief This functions collects all the datas entered by the user
    @param the instance
    @return Nothing
    """
    def on_button_click(self):

        # Print the chosen data
        print("User :", self.user_entry.get())
        print("Configuration :", self.configuration_combobox.get())
        print("Session :", self.session_entry.get())
        print("Participant :", self.participant_entry.get())



        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="prismathome"
        )
        cursor = conn.cursor()

        # Exécutez une requête
        query = "INSERT INTO observation (id_observation, id_system, participant, id_config, id_session, session_label)VALUES('1', %s, %s, %s, %s, %s)"
        cursor.execute(query, (self.participant_entry.get(), globals.global_id_config,  self.session_entry.get()))
        conn.commit()

    def get_config(self):
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="prisme_home_1"
        )
        cursor = conn.cursor()

        # Execute a request
        query = "SELECT label FROM configuration "
        cursor.execute(query,)
        return cursor.fetchall()
