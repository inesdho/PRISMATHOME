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
        # TODO paul I guess ? remplacer le default texte par la valeur que tu as crée de l'utilisateur de la session
        self.user_entry = EntryManager(self.frame, min=1, max=30, has_width=30, default_text="User")


        # Configuration list
        options = self.get_config()
        configuration_label = ttk.Label(self.frame, text="Configuration", font=globals.global_font_title1)
        configuration_label.pack()
        self.configuration_combobox = ttk.Combobox(self.frame, values=options, width=29)
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

        # Print the chosen data
        print("User :", self.user_entry.get())
        print("Configuration :", self.configuration_combobox.get())
        print("Session :", self.session_entry.get())
        print("Participant :", self.participant_entry.get())

        id_system = self.get_id_system()
        id_conf = self.get_config_by_id(self.configuration_combobox.get())
        id_session = self.get_id_session() + 1

        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Q3fhllj2",
            database="prisme_home_1"
        )
        cursor = conn.cursor()

        # Exécutez une requête d'insertion
        query = """
        INSERT INTO observation (id_system, participant, id_config, id_session, session_label, active)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (id_system, self.participant_entry.get(), id_conf, id_session, self.session_entry.get(), 0))

        # Récupérez l'ID de la nouvelle observation
        globals.global_new_id_observation = cursor.lastrowid

        # Confirmez les modifications dans la base de données
        conn.commit()

        # Affichez l'ID de la nouvelle observation
        print("L'ID de la nouvelle observation est :", globals.global_new_id_observation)

        # Assurez-vous de fermer le curseur et la connexion
        cursor.close()
        conn.close()

    def get_config(self):
        """!
        @brief This functions returns the label of the configurations stored in the database
        @param self : the instance
        @return the label of the configurations stored in the database
        """
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Q3fhllj2",
            database="prisme_home_1"
        )
        cursor = conn.cursor()

        # Execute a request
        query = "SELECT label FROM configuration"
        cursor.execute(query)
        # Extract the first element of each tuple to get the labels as a list of strings
        config_labels = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return config_labels

    def get_config_by_id(self, label):
        """!
        @brief This functions returns the id of the configuration that was selected by the user depending on its label.
        @param self : the instance
        @param label : the label of the configuration
        @return the id of the configuration selected by the user
        """
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Q3fhllj2",
            database="prisme_home_1"
        )
        cursor = conn.cursor()

        # Execute a request
        query = "SELECT id_config FROM configuration WHERE label=%s"
        cursor.execute(query, (label,))  # Pass label as a tuple
        result = cursor.fetchone()  # Fetch the first result
        cursor.close()
        conn.close()
        globals.global_id_config_selectionned=result[0]
        return globals.global_id_config_selectionned if result else None

    def get_id_system(self):
        """!
        @brief This functions returns the id of the system
        @param self : the instance
        @return the id of the system
        """
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Q3fhllj2",
                database="prisme_home_1"
            )
            cursor = conn.cursor()

            # Check if 'system' is a table in your database and escape it with backticks if necessary
            query = "SELECT id_system FROM `system`"
            cursor.execute(query)
            result = cursor.fetchone()  # Fetch the result
            return result[0] if result else None
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()

    def get_id_session(self):
        """!
        @brief This functions returns the id of the last session created in the database
        @param self : the instance
        @return the id of the last session created in the database
        """
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Q3fhllj2",
            database="prisme_home_1"
        )
        cursor = conn.cursor()
        label = self.configuration_combobox.get()
        id_conf = self.get_config_by_id(label)  # Ensure id_conf is set correctly

        # Make sure the query includes both placeholders
        query = "SELECT COUNT(id_session) FROM observation WHERE participant=%s AND id_config=%s"
        cursor.execute(query, (self.participant_entry.get(), id_conf))  # Pass participant and id_conf as a tuple
        result = cursor.fetchone()  # Fetch the first result
        cursor.close()
        conn.close()
        return result[0] if result else None

