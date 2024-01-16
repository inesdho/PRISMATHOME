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
from model import local


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
        self.frame.pack(fill=tk.BOTH, expand=True)

    def show_page(self):
        """!
        @brief The show_page function creates and displays all the elements of the "create or modify a configuration" page
        @param self : the instance
        @return Nothing
        """
        # Left Frame for configuration modification
        self.left_frame = tk.Frame(self.master, bd=2, relief="sunken", padx=5, pady=5)
        self.left_frame.place(relx=0.02, rely=0.09, relwidth=0.46, relheight=0.50)

        # Creates the elements related to the selection of a configuration to modify
        label_scenario_name = tk.Label(self.left_frame, text="Scenario name :", font=globals.global_font_text)
        label_scenario_name.pack(anchor="nw")

        # Get the configuration labels and ids
        configurations = local.get_config_labels_ids()

        if configurations is not None:
            # Creation of a tuple list
            self.configuration_values = [(config['label'], config['id_config']) for config in configurations]

            # Creation of a combobox with the list of configuration labels
            self.configuration_combobox = ttk.Combobox(self.left_frame, width=30)
            self.configuration_combobox['values'] = [label for label, id_config in self.configuration_values]
            self.configuration_combobox.pack(fill="x")
        else:
            configurations = []
            self.configuration_combobox = ttk.Combobox(self.frame, values=configurations, width=29)
            self.configuration_combobox.pack(pady=10)

        # Right Frame for configuration Creation
        self.right_frame = tk.Frame(self.master, bd=2, relief="sunken", padx=5, pady=5)
        self.right_frame.place(relx=0.50, rely=0.09, relwidth=0.48, relheight=0.50)

        # Creates the elemtents related to the creation of a new configuration
        tk.Label(self.right_frame, text="Scenario name :", font=globals.global_font_text).pack(anchor="nw")
        self.right_frame.update()
        self.name_entry = EntryManager(self.right_frame, min=1, max=30, has_width=self.right_frame.winfo_width(),
                                       default_text="Enter label")

        tk.Label(self.right_frame, text="Description :", font=globals.global_font_text).pack(anchor="nw")
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

    def on_click_modify_button(self):
        globals.global_id_config_modify = self.get_selected_id_config()