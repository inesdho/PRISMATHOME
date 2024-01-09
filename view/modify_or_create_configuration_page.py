"""!
@file modify_or_create_configuration_page.py
@brief This file will contain all the widgets and functions related to the "create or modify a configuration"
page itself
@author Naviis-Brain
@version 1.0
@date
"""
import tkinter as tk
from tkinter import ttk

import mysql.connector
from ttkthemes.themed_style import ThemedStyle
import globals

from view.login_as_admin_page import LoginAsAdministrator
from controller.entry_manager import EntryManager
from controller.text_manager import TextManager

class ModifyOrCreateConfiguration:

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

    def show_page(self):
        """!
        @brief The show_page function creates and displays all the elements of the "create or modify a configuration" page
        @param self : the instance
        @return Nothing
        """
        self.frame = ttk.Frame(self.master)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Left Frame for configuration modification
        self.left_frame = tk.Frame(self.master, bd=2, relief="sunken", padx=5, pady=5)
        self.left_frame.place(relx=0.02, rely=0.09, relwidth=0.46, relheight=0.50)

        # Creates the elements related to the selection of a configuration to modify
        label_scenario_name = tk.Label(self.left_frame, text="Scenario name :")
        label_scenario_name.pack(anchor="nw")
        self.scenario_combobox = ttk.Combobox(self.left_frame, values=["Example", "Exemple 2", "Exemple 3"],
                                              state="readonly",
                                              width=30)
        self.scenario_combobox.set("Example")
        self.scenario_combobox.pack(fill="x")

        # Right Frame for configuration Creation
        self.right_frame = tk.Frame(self.master, bd=2, relief="sunken", padx=5, pady=5)
        self.right_frame.place(relx=0.50, rely=0.09, relwidth=0.48, relheight=0.50)

        # Creates the elemtents related to the creation of a new configuration
        tk.Label(self.right_frame, text="Scenario name :").pack(anchor="nw")
        self.right_frame.update()
        self.name_entry = EntryManager(self.right_frame, min=1, max=30, has_width=self.right_frame.winfo_width(),
                                       default_text="Enter label")

        tk.Label(self.right_frame, text="Description :").pack(anchor="nw")
        # Create a Text widget for multi-line text entry
        self.description_text_entry = TextManager(self.right_frame, min=1, max=800,
                                                  has_width=self.right_frame.winfo_width(),
                                                  has_height=5, default_text="Enter description")

    def save_label_description_id_of_config_into_globals(self):
        """!
        @brief This function is called when the user clicks on a button to create a new configuration and saves the
        label of the new configuration and its description into global variables.
        @param self : the instance
        @return Nothing
        """

        # Saving the variables into global variables
        globals.global_scenario_name_configuration = self.name_entry.get()
        globals.global_description_configuration = self.description_text_entry.get()

        print(globals.global_scenario_name_configuration)
        print(globals.global_description_configuration)

        num_config = self.get_number_config_create_by_admin(globals.global_id_user) + 1

        id_config = str(globals.global_id_user) + "-" + str(num_config)
        globals.global_id_config = id_config
        print("valeur de l'id user")
        print(globals.global_id_user)

    def does_label_config_already_exists(self):
        """!
        @brief This function checks that the label of the configuration is not already used in the database. For this
        purpose it will count the number of occurrence of the label in the table configuration.
        @param self : the instance
        @return If the label is already used, this functions returns True, otherwise False.
        """
        # Connexion to the MySQL database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Q3fhllj2",
            database="prisme_home_1"
        )
        cursor = conn.cursor()

        # Execute a request
        query = "SELECT COUNT(*) FROM configuration WHERE label = %s"
        cursor.execute(query, (self.name_entry.get(),))

        # Get the result
        count = cursor.fetchone()[0]

        # Close the connexion to the database
        cursor.close()
        conn.close()

        # Return False if no other configuration has the same name, return True otherwise
        if count == 0:
            return False
        else:
            return True

    def get_number_config_create_by_admin(self, id_user):
        """!
        @brief This function is called when the user clicks on a button to modify a configuration and fetch said
        configuration in the database
        @param self : the instance
        @param id_user : the id of the user wanting to modify the configuration
        @return Nothing
        """

        # Connexion to the MySQL database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Q3fhllj2",
            database="prisme_home_1"
        )
        cursor = conn.cursor()

        # Execute a request
        query = "SELECT COUNT(*) FROM configuration WHERE id_user = %s"
        cursor.execute(query, (id_user,))

        # Get the result
        count = cursor.fetchone()[0]

        # Close the connexion to the database
        cursor.close()
        conn.close()

        return count

    def log_out_the_admin(self):
        """!
        @brief This function is called when the admin logs out and will change the connection status to False
        @param self : the instance
        @return Nothing
        """
        # Connexion to the MySQL database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Q3fhllj2",
            database="prisme_home_1"
        )
        cursor = conn.cursor()

        # Update the connexion status in the database
        query_update = "UPDATE prisme_home_1.user SET connected=0 WHERE login=%s AND password=%s"
        cursor.execute(query_update, (globals.global_connected_admin_login, globals.global_connected_admin_password))
        conn.commit()

        # Deleteing the login and the password of the connected admin
        globals.global_connected_admin_login = None
        globals.global_connected_admin_password = None

        # Close the connexion to the database
        cursor.close()
        conn.close()

    def clear_page(self):
        """!
        @brief This function clears the entire "new observation" page
        @param self : the instance
        @return Nothing
        """
        # Destroy the frame
        self.frame.destroy()
        self.right_frame.destroy()
        self.left_frame.destroy()
