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
from controller.input_manager import Input

class ModifyOrCreateConfiguration:

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
    @brief The show_page function creates and displays all the elements of the "create or modify a configuration" page
    @param the instance
    @return Nothing
    """
    def show_page(self):
        self.frame = ttk.Frame(self.master)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Left Frame for copnfiguration modification
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
        self.name_entry = Input(self.right_frame, has_width=self.right_frame.winfo_width(), min=0, max=30)

        tk.Label(self.right_frame, text="Description :").pack(anchor="nw")
        # Create a Text widget for multi-line text entry
        self.description_text_entry = tk.Text(self.right_frame, height=5)  # Height is set to 5 lines
        self.description_text_entry.pack(fill="x")

    """!
    @brief This fuctions is called when the user clicks on a button to create a new configuration and saves the label of
    the new configuration and it's description into global variables
    @param the instance
    @return Nothing
    """
    def on_create_configuration_button_click(self):

        # Saving the variables into global variables
        globals.global_scenario_name_configuration = self.name_entry.get()
        globals.global_description_configuration = self.description_text_entry.get("1.0", "end-1c")

        print(globals.global_scenario_name_configuration)

        # RETURN TRUE POUR TESTER LES REDIRECTIONS SANS LA BDD
        # return True

        num_config = self.get_number_config_create_by_admin(globals.global_id_user) + 1

        id_config = str(globals.global_id_user) + "-" + str(num_config)
        globals.global_id_config = id_config
        print("valeur de l'id user")
        print(globals.global_id_user)

    """!
    @brief This fuctions is called when the user clicks on a button to modify a configuration and fetch said 
    configuration in the database
    @param the instance, id_ser -> the id of the user wanting to modify the configuration
    @return Nothing
    """
    def get_number_config_create_by_admin(self, id_user):

        # RETURN TRUE POUR TESTER LES REDIRECTIONS SANS LA BDD
        # return True

        # Connexion to the MySQL database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="prismathome"
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

    """!
    @brief This functions clears the entire "new observation" page
    @param the instance
    @return Nothing
    """
    def clear_page(self):
        # Destroy the frame
        self.frame.destroy()
        self.right_frame.destroy()
        self.left_frame.destroy()
