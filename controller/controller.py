"""!
@file controller.py
@brief This file will contain all the redirection between the pages of the user and admin interface
@author Naviis-Brain
@version 1.0
@date
"""

import tkinter as tk
from tkinter import ttk

from tkinter.messagebox import *
from ttkthemes import ThemedTk, ThemedStyle
from view.new_observation_page import NewObservation
from view.login_as_admin_page import LoginAsAdministrator
from view.modify_or_create_configuration_page import ModifyOrCreateConfiguration
from view.summary_page import Summary
from view.selection_sensor_quantity_page import QuantitySensor
from view.labellisation_sensor_page import LabelisationSensor
from view.sensor_pairing_management_page import SensorPairingManagement


class App(ThemedTk):

    """!
    @brief The __init__ function create and set the theme and parameter of the window that will contain the pages of the
    user interface
    @param the instance
    @return Nothing
    """
    def __init__(self):
        ThemedTk.__init__(self)
        self.title("PRISM@Home")
        self.attributes('-fullscreen', True)
        self.bind('<Escape>', lambda e: self.attributes('-fullscreen', False))

        # Theme of the application
        self.style = ThemedStyle(self)
        self.style.set_theme("breeze")  # Write the theme you would like

        self.show_frame()

    """!
    @brief The show_frame function allows the creation of the main frame and call the new observation page
    @param the instance
    @return Nothing
    """
    def show_frame(self):

        # Creating main frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Call the New observation window in order to
        self.call_new_observation_page()

    """!
    @brief This function initialises and calls new_observation_page.py in order to show the page and also adds 
    navigation button
    @param the instance 
    @return Nothing
    """
    def call_new_observation_page(self):
        # Redirecting to the login page
        new_observation_page = NewObservation(self)
        new_observation_page.show_page()

        # Redirection to login as an admin button
        ttk.Button(self.main_frame, text="Login as administrator",
                   command=lambda: self.redirect_to_login_as_admin_from_new_observation(new_observation_page)).place(
            relx=0.9, rely=0.1)

        # Redirection to login as an admin button
        ttk.Button(new_observation_page.frame, text="Import configuration",
                   command=lambda: self.redirect_to_pairing_from_anywhere(new_observation_page)).pack()

    """!
    @brief This function clears the previous page before calling the new observation page
    @param the instance, the previous page
    @return Nothing
    """
    def redirect_to_new_observation_from_anywhere(self, page):

        # Clear the previous page content
        self.clear_the_page(page)

        # Creation of a main frame
        self.create_new_main_frame()

        self.call_new_observation_page()

    """!
    @brief This function clears the previous pagein order to display the content of the pairing page and adds navigation
    buttons to the page
    @param the instance, the previous page
    @return Nothing
    """
    def redirect_to_pairing_from_anywhere(self, page):

        # /!\ à supprimer test
        page.on_button_click()

        # Clear the previous page content
        self.clear_the_page(page)

        # Calling the sensor pairing page
        sensor_pairing_page = SensorPairingManagement(self)
        sensor_pairing_page.show_page()

        # Creation of a main frame
        self.create_new_main_frame()

        # Back button
        back_button = ttk.Button(self.main_frame, text="Back",
                                 command=lambda: self.redirect_to_new_observation_from_anywhere(sensor_pairing_page))
        back_button.pack(side=tk.LEFT, padx=10, expand=True)

        # Redirection to summary to confirm the configuration
        next_button = ttk.Button(self.main_frame, text="Next",
                                 command=lambda: self.redirect_to_summary_from_pairing(sensor_pairing_page))
        next_button.pack(side=tk.RIGHT, padx=10, expand=True)

    """!
    @brief This function clears the new observation page in order to display the content of the the login as admin page 
    and adds navigations buttons to the page
    @param the instance, the previous page
    @return Nothing
    """
    def redirect_to_login_as_admin_from_new_observation(self, new_observation_page):

        # Clear the previous page content
        self.clear_the_page(new_observation_page)

        # Creation of a main frame
        self.create_new_main_frame()

        # Redirecting to the login page
        login_as_admin_page = LoginAsAdministrator(self.master)
        login_as_admin_page.show_page()

        # Connection button
        ttk.Button(login_as_admin_page.frame, text="Connexion",
                   command=lambda: self.connexion_button_clic(login_as_admin_page)).pack(pady=20)

        # Cancel button to redirect to the new observation page
        ttk.Button(self.main_frame, text="Cancel",
                   command=lambda: self.redirect_to_new_observation_from_anywhere(login_as_admin_page)).place(
            relx=0.9,rely=0.1)

    """!
    @brief This function calls the connexion_admin function located in the "login as admin page" in order to check if 
    the login and password entered by the user are correct
    @param the instance, the login as admin page
    @return Nothing
    """
    def connexion_button_clic(self, login_as_admin_page):

        # Checking if the login and password are correct
        if login_as_admin_page.connexion_admin() == False:
            # If they are not correct show an error message
            showerror("Error", "The login or the password is incorrect")
        else:
            # If they are correct the user is redirected to the "modify or create a configuration page"
            self.redirect_to_modify_or_create_configuration_from_anywhere(login_as_admin_page)
            pass

    """!
    @brief This function clears the previous page in order to display the content of the "modify or create a 
    configuration page" and adds navigations buttons
    @param the instance, the previous page
    @return Nothing
    """
    def redirect_to_modify_or_create_configuration_from_anywhere(self, page):

        # Clear the previous page content
        self.clear_the_page(page)

        # Creation of a main frame
        self.create_new_main_frame()

        # Creation of the "modify or create configuration page"
        modify_or_create_configuration_page = ModifyOrCreateConfiguration(self.master)
        modify_or_create_configuration_page.show_page()

        # Logout Button
        logout_button = ttk.Button(self.main_frame, text="Log out",
                                   command=lambda: self.redirect_to_new_observation_from_anywhere(
                                       modify_or_create_configuration_page))
        logout_button.place(relx=0.9, rely=0.01)

        # Modify Button
        # TODO Modifier la redirection pour qu'elle prenne en compte le fait que là on va éditer une config existante
        modify_button = ttk.Button(modify_or_create_configuration_page.left_frame, text="Modify the configuration",
                                   command=lambda: self.redirect_to_selection_sensor_quantity_from_create_a_config(
                                       modify_or_create_configuration_page))
        modify_button.pack(side="bottom", fill="x")

        # Create a new configuration button
        create_button = ttk.Button(modify_or_create_configuration_page.right_frame, text="Create a configuration",
                                   command=lambda: self.redirect_to_selection_sensor_quantity_from_create_a_config(
                                       modify_or_create_configuration_page))
        create_button.pack(side="bottom", fill="x")

    """!
    @brief This function calls the function located in summary that will save the config into the BDD and then calls the
    function that display the modify or create a configuration page
    @param the instance, the summary page
    @return Nothing
    """
    def redirect_to_modify_or_create_configuration_after_config_validation(self, summary_page):

        # Log the data into the BDD
        summary_page.print_sensor_data()

        # Go back to the "modify or create a configuration page"
        self.redirect_to_modify_or_create_configuration_from_anywhere(summary_page)

    """!
    @brief This function clears the previous page in order to display the content of the "selection sensro quantity" and
    adds navigations buttons. It also create a nex configuration in the BDD
    @param the instance, the create or modify a configuration page
    @return Nothing
    """
    def redirect_to_selection_sensor_quantity_from_create_a_config(self, create_a_config_page):

        # Create a new configuration in the BDD
        create_a_config_page.on_create_configuration_button_click()

        # Clear the previous page content
        self.clear_the_page(create_a_config_page)

        selction_sensor_quantity_page = QuantitySensor(self)
        selction_sensor_quantity_page.show_page()

        # Creation of a main frame
        self.create_new_main_frame()

        # Add buttons
        back_button = ttk.Button(self.main_frame, text="Back",
                                 command=lambda: self.redirect_to_modify_or_create_configuration_from_anywhere(
                                     selction_sensor_quantity_page))
        back_button.pack(side=tk.LEFT, padx=10, expand=True)

        next_button = ttk.Button(self.main_frame, text="Next",
                                 command=lambda: self.redirect_to_labellisation_sensor_from_sensor_quantity(
                                     selction_sensor_quantity_page))
        next_button.pack(side=tk.RIGHT, padx=10, expand=True)

    def redirect_to_selection_sensor_quantity_from_anywhere(self, page):

        # Clear the previous page content
        self.clear_the_page(page)

        selction_sensor_quantity_page = QuantitySensor(self)
        selction_sensor_quantity_page.show_page()

        # Creation of a main frame
        self.create_new_main_frame()

        # Add buttons
        back_button = ttk.Button(self.main_frame, text="Back",
                                 command=lambda: self.redirect_to_modify_or_create_configuration_from_anywhere(
                                     selction_sensor_quantity_page))
        back_button.pack(side=tk.LEFT, padx=10, expand=True)

        next_button = ttk.Button(self.main_frame, text="Next",
                                 command=lambda: self.redirect_to_labellisation_sensor_from_sensor_quantity(
                                     selction_sensor_quantity_page))
        next_button.pack(side=tk.RIGHT, padx=10, expand=True)

    def redirect_to_labellisation_sensor_from_sensor_quantity(self, selction_sensor_quantity_page):

        selction_sensor_quantity_page.on_next_button_click()

        # Clear the previous page content
        self.clear_the_page(selction_sensor_quantity_page)

        labellisation_sensor_page = LabelisationSensor(self)
        labellisation_sensor_page.show_page()

        # Creation of a main frame
        self.create_new_main_frame()

        # Add buttons
        back_button = ttk.Button(self.main_frame, text="Back",
                                 command=lambda: self.redirect_to_selection_sensor_quantity_from_anywhere(
                                     labellisation_sensor_page))
        back_button.pack(side=tk.LEFT, padx=10, expand=True)

        next_button = ttk.Button(self.main_frame, text="Next",
                                 command=lambda: self.redirect_to_summary_from_labellisation(labellisation_sensor_page))
        next_button.pack(side=tk.RIGHT, padx=10, expand=True)

    def redirect_to_labellisation_sensor_from_summary(self, summary_page):

        # Clear the previous page content
        self.clear_the_page(summary_page)

        labellisation_sensor_page = LabelisationSensor(self)
        labellisation_sensor_page.show_page()

        # Creation of a main frame
        self.create_new_main_frame()

        # Add buttons
        back_button = ttk.Button(self.main_frame, text="Back",
                                 command=lambda: self.redirect_to_selection_sensor_quantity_from_anywhere(
                                     labellisation_sensor_page))
        back_button.pack(side=tk.LEFT, padx=10, expand=True)

        next_button = ttk.Button(self.main_frame, text="Next",
                                 command=lambda: self.redirect_to_summary_from_labellisation(labellisation_sensor_page))
        next_button.pack(side=tk.RIGHT, padx=10, expand=True)

    def redirect_to_summary_from_labellisation(self, labellisation_sensor_page):

        labellisation_sensor_page.print_sensor_data()

        # Clear the previous page content
        self.clear_the_page(labellisation_sensor_page)

        summary_page = Summary(self)
        summary_page.show_page(False)

        # Creation of a main frame
        self.create_new_main_frame()

        # Cancel button
        concenl_button = ttk.Button(self.main_frame, text="Cancel",
                                    command=lambda: self.redirect_to_modify_or_create_configuration_from_anywhere(
                                        summary_page))
        concenl_button.pack(side=tk.LEFT, padx=10, expand=True)

        # Back button
        back_button = ttk.Button(self.main_frame, text="Back",
                                 command=lambda: self.redirect_to_labellisation_sensor_from_summary(summary_page))
        back_button.pack(side=tk.LEFT, padx=10, expand=True)

        # Validate configuration button
        back_button = ttk.Button(self.main_frame, text="Validate configuration",
                                 command=lambda: self.redirect_to_modify_or_create_configuration_after_config_validation
                                     (summary_page))
        back_button.pack(side=tk.LEFT, padx=10, expand=True)

    def redirect_to_summary_from_pairing(self, sensor_pairing_page):

        # Clear the previous page content
        self.clear_the_page(sensor_pairing_page)

        summary_page = Summary(self)
        summary_page.show_page(True)

        # Creation of a main frame
        self.create_new_main_frame()

        # Cancel button
        cancel_button = ttk.Button(self.main_frame, text="Exit",
                                    command=lambda: self.redirect_to_new_observation_from_anywhere(summary_page))
        cancel_button.pack(side=tk.LEFT, padx=10, expand=True)

        # Back button
        back_button = ttk.Button(self.main_frame, text="Back",
                                 command=lambda: self.redirect_to_pairing_from_anywhere(summary_page))
        back_button.pack(side=tk.LEFT, padx=10, expand=True)

        # Start observation button
        back_button = ttk.Button(self.main_frame, text="Start observation",
                                 command=lambda: self.redirect_to_modify_or_create_configuration(summary_page))
        back_button.pack(side=tk.LEFT, padx=10, expand=True)

    def clear_the_page(self, page):
        # Clear the previous page content and the main frame in order to be sure that there is nothing left
        page.clear_page()
        self.main_frame.destroy()

    def create_new_main_frame(self):
        # Creation of a main frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
