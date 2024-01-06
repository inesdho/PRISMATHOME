"""!
@file controller.py
@brief This file will contain all the redirection between the pages of the user and admin interface
@author Naviis-Brain
@version 1.0
@date
"""

import tkinter as tk
from tkinter import ttk, messagebox

from ttkthemes import ThemedTk, ThemedStyle
from view.new_observation_page import NewObservation
from view.login_as_admin_page import LoginAsAdministrator
from view.modify_or_create_configuration_page import ModifyOrCreateConfiguration
from view.summary_admin_page import SummaryAdmin
from view.summary_user_page import SummaryUser
from view.summary_observation_page import SummaryObservation
from view.selection_sensor_quantity_page import QuantitySensor
from view.labellisation_sensor_page import LabelisationSensor
from view.sensor_pairing_management_page import SensorPairingManagement
import webbrowser



class App(ThemedTk):

    def __init__(self):
        """!
        @brief The __init__ function creates and set the theme and parameter of the window that will contain the pages of the
        user interface
        @param the instance
        @return Nothing
        """
        ThemedTk.__init__(self)
        self.title("PRISM@Home")
        self.attributes('-fullscreen', True)
        self.bind('<Escape>', lambda e: self.attributes('-fullscreen', False))

        # Theme of the application
        self.style = ThemedStyle(self)
        self.style.set_theme("breeze")  # Write the theme you would like

        self.show_frame()

    def show_frame(self):
        """!
        @brief The show_frame function allows the creation of the main frame and call the new observation page
        @param the instance
        @return Nothing
        """

        # Creating main frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Call the New observation window in order to
        self.call_new_observation_page()

    def call_new_observation_page(self):
        """!
        @brief This function initialises and calls new_observation_page.py in order to show the page and also adds
        navigation button
        @param the instance
        @return Nothing
        """
        # Redirecting to the login page
        new_observation_page = NewObservation(self)
        new_observation_page.show_page()

        # Redirection to login as an admin button
        ttk.Button(self.main_frame, text="Login as administrator",
                   command=lambda: self.redirect_to_login_as_admin_from_anywhere(new_observation_page)).place(
            relx=0.9, rely=0.1)

        # Redirection to login as an admin button
        ttk.Button(new_observation_page.frame, text="Import configuration",
                   command=lambda: self.redirect_to_pairing_from_new_observation(new_observation_page)).pack()

    def redirect_to_new_observation_from_anywhere(self, page):
        """!
        @brief This function clears the previous page before calling the new observation page
        @param the instance, the previous page
        @return Nothing
        """

        # Clear the previous page content
        self.clear_the_page(page)

        # Creation of a main frame
        self.create_new_main_frame()

        self.call_new_observation_page()

    def redirect_to_pairing_from_new_observation(self, new_observation_page):
        """!
        @brief This function clears the previous page in order to display the content of the pairing page and adds navigation
        buttons to the page
        @param the instance, the previous page
        @return Nothing
        """

        new_observation_page.on_import_button_click()
        # Clear the previous page content
        self.clear_the_page(new_observation_page)

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
                                 command=lambda: self.redirect_to_summary_user_from_anywhere(sensor_pairing_page))
        next_button.pack(side=tk.RIGHT, padx=10, expand=True)


    def redirect_to_pairing_from_user_summary(self, user_summary_page):
        """!
        @brief This function clears the previous page in order to display the content of the pairing page and adds navigation
        buttons to the page
        @param the instance, the previous page
        @return Nothing
        """

        # Clear the previous page content
        self.clear_the_page(user_summary_page)

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
                                 command=lambda: self.redirect_to_summary_user_from_anywhere(sensor_pairing_page))
        next_button.pack(side=tk.RIGHT, padx=10, expand=True)



    def redirect_to_login_as_admin_from_anywhere(self, page):
        """!
        @brief This function clears the new observation page in order to display the content of the the login as admin page
        and adds navigations buttons to the page
        @param the instance, the previous page
        @return Nothing
        """

        # Clear the previous page content
        self.clear_the_page(page)

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

    def connexion_button_clic(self, login_as_admin_page):
        """!
        @brief This function calls the connexion_admin function located in the "login as admin page" in order to check if
        the login and password entered by the user are correct
        @param the instance, the login as admin page
        @return Nothing
        """

        # Checking if the login and password are correct
        if login_as_admin_page.connexion_admin():
            # If they are correct the user is redirected to the "modify or create a configuration page"
            self.redirect_to_modify_or_create_configuration_from_anywhere(login_as_admin_page)


    def redirect_to_modify_or_create_configuration_from_anywhere(self, page):
        """!
        @brief This function clears the previous page in order to display the content of the "modify or create a
        configuration page" and adds navigations buttons
        @param the instance, the previous page
        @return Nothing
        """

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

    def redirect_to_modify_or_create_configuration_after_config_validation(self, summary_admin_page):
        """!
        @brief This function calls the function located in summary admin that will save the config into the database and
        then calls the function that display the modify or create a configuration page
        @param the instance, the summary admin page
        @return Nothing
        """

        # Log the data into the database
        summary_admin_page.validate_conf()

        # Go back to the "modify or create a configuration page"
        self.redirect_to_modify_or_create_configuration_from_anywhere(summary_admin_page)

    def redirect_to_selection_sensor_quantity_from_create_a_config(self, create_a_config_page):
        """!
        @brief This function clears the previous page in order to display the content of the "selection sensor quantity" and
        adds navigations buttons. It also create a nex configuration in the database
        @param the instance, the create or modify a configuration page
        @return Nothing
        """

        # Create a new configuration in the database
        create_a_config_page.on_create_configuration_button_click()

        # Clear the previous page content
        self.clear_the_page(create_a_config_page)

        # Creattion of the "selection sensor quantity" page
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
                                 command=lambda: self.check_if_user_chose_at_least_one_sensor(
                                     selction_sensor_quantity_page))
        next_button.pack(side=tk.RIGHT, padx=10, expand=True)

    def redirect_to_selection_sensor_quantity_from_anywhere(self, page):
        """!
        @brief This function clears the previous page in order to display the content of the "selection sensor quantity"
        page and adds navigations buttons.
        @param the instance, the previous page
        @return Nothing
        """

        # Clear the previous page content
        self.clear_the_page(page)

        # Creation of the "selection sensor quantity" page
        selection_sensor_quantity_page = QuantitySensor(self)
        selection_sensor_quantity_page.show_page()

        # Creation of a main frame
        self.create_new_main_frame()

        # Add buttons
        back_button = ttk.Button(self.main_frame, text="Back",
                                 command=lambda: self.redirect_to_modify_or_create_configuration_from_anywhere(
                                     selection_sensor_quantity_page))
        back_button.pack(side=tk.LEFT, padx=10, expand=True)

        next_button = ttk.Button(self.main_frame, text="Next",
                                 command=lambda: self.check_if_user_chose_at_least_one_sensor(
                                     selection_sensor_quantity_page))
        next_button.pack(side=tk.RIGHT, padx=10, expand=True)

    def check_if_user_chose_at_least_one_sensor(self, selection_sensor_quantity_page):
        """!
        @brief This checks if the user selected at least one sensor before they are redirected to the labellisation page.
        If no sensor was selected, an error message is displayed and the usr can't access to the next page.
        @param the instance, the selection_sensor_quantity_page
        @return Nothing
        """
        if selection_sensor_quantity_page.chose_at_least_one_sensor():
            self.redirect_to_labellisation_sensor_from_sensor_quantity(selection_sensor_quantity_page)
        else:
            messagebox.showerror("Error", "Please select at least one sensor")



    def redirect_to_labellisation_sensor_from_sensor_quantity(self, selection_sensor_quantity_page):
        """!
        @brief This function clears the previous page in order to display the content of the "labellisation sensor"
        page and adds navigations buttons. It also allows to save into global variables the data entered by the user in the
        previous page
        @param the instance, the selection sensor quantity page
        @return Nothing
        """

        # Calls this function in order to store into global variables the datas entered by the user in the sensor
        # quantity page
        selection_sensor_quantity_page.on_next_button_click()

        # Clear the previous page content
        self.clear_the_page(selection_sensor_quantity_page)

        # Creation of the "creation of the labellisation sensor" page
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
                                 command=lambda: self.redirect_to_summary_admin_from_labellisation(labellisation_sensor_page))
        next_button.pack(side=tk.RIGHT, padx=10, expand=True)

    def redirect_to_labellisation_sensor_from_summary_admin(self, summary_admin_page):
        """!
        @brief This function clears the previous page in order to display the content of the "labellisation sensor"
        page and adds navigations buttons.
        @param the instance, the summary admin page
        @return Nothing
        """

        # Clear the previous page content
        self.clear_the_page(summary_admin_page)

        # Creation of the "creation of the labellisation sensor" page
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
                                 command=lambda: self.redirect_to_summary_admin_from_labellisation(labellisation_sensor_page))
        next_button.pack(side=tk.RIGHT, padx=10, expand=True)

    def redirect_to_summary_admin_from_labellisation(self, labellisation_sensor_page):
        """!
        @brief This function clears the previous page in order to display the content of the "summary admin"
        page and adds navigations buttons. It also saves the data in the "labellisation" page
        entered by the user into global variables
        @param the instance, the labellisation page
        @return Nothing
        """

        # Saves the data entered by the user in the labellisation page into global variables
        labellisation_sensor_page.get_sensor_data()

        # Clear the previous page content
        self.clear_the_page(labellisation_sensor_page)

        # Creation of the summary admin page
        summary_admin_page = SummaryAdmin(self)
        summary_admin_page.show_page()

        # Creation of a main frame
        self.create_new_main_frame()

        # Cancel button
        concenl_button = ttk.Button(self.main_frame, text="Cancel",
                                    command=lambda: self.redirect_to_modify_or_create_configuration_from_anywhere(
                                        summary_admin_page))
        concenl_button.pack(side=tk.LEFT, padx=10, expand=True)

        # Back button
        back_button = ttk.Button(self.main_frame, text="Back",
                                 command=lambda: self.redirect_to_labellisation_sensor_from_summary_admin(summary_admin_page))
        back_button.pack(side=tk.LEFT, padx=10, expand=True)

        # Validate configuration button
        back_button = ttk.Button(self.main_frame, text="Validate configuration",
                                 command=lambda: self.redirect_to_modify_or_create_configuration_after_config_validation
                                     (summary_admin_page))
        back_button.pack(side=tk.LEFT, padx=10, expand=True)

    def redirect_to_summary_user_from_anywhere(self, page):
        """!
        @brief This function clears the previous page in order to display the content of the "summary user"
        page and adds navigations buttons.
        @param the instance, the pairing page
        @return Nothing
        """

        # Clear the previous page content
        self.clear_the_page(page)

        # Creation of the summary user page
        summary_user_page = SummaryUser(self)
        summary_user_page.show_page()

        # Creation of a main frame
        self.create_new_main_frame()

        # Cancel button
        cancel_button = ttk.Button(self.main_frame, text="Exit",
                                    command=lambda: self.redirect_to_new_observation_from_anywhere(summary_user_page))
        cancel_button.pack(side=tk.LEFT, padx=10, expand=True)

        # Back button
        back_button = ttk.Button(self.main_frame, text="Back",
                                 command=lambda: self.redirect_to_pairing_from_user_summary(summary_user_page))
        back_button.pack(side=tk.LEFT, padx=10, expand=True)

        # Start observation button
        back_button = ttk.Button(self.main_frame, text="Start observation",
                                 command=lambda: self.redirect_to_summary_observation_from_summary_user(summary_user_page))
        back_button.pack(side=tk.LEFT, padx=10, expand=True)


    def redirect_to_summary_observation_from_summary_user(self, summary_user_page):
        """!
        @brief This function clears the previous page in order to display the content of the "summary obsevation"
        page and adds navigations buttons.
        @param the instance, the pairing page
        @return Nothing
        """

        # Clear the previous page content
        self.clear_the_page(summary_user_page)

        # Creation of the summary observation page
        summary_observation_page = SummaryObservation(self)
        summary_observation_page.show_page()

        # Creation of a main frame
        self.create_new_main_frame()

        # Redirection to the PHPMyAdmin
        cancel_button = ttk.Button(self.main_frame, text="Get data through PHPMyAdmin",
                                   command=lambda: webbrowser.open('http://localhost/phpmyadmin/'))
        cancel_button.pack(side=tk.LEFT, padx=10, expand=True)

        # Stop observation button
        back_button = ttk.Button(self.main_frame, text="Stop observation",
                                 command=lambda: self.redirect_to_summary_user_from_anywhere(summary_observation_page))
        back_button.pack(side=tk.LEFT, padx=10, expand=True)

    def clear_the_page(self, page):
        """!
        @brief This function calls the clear page function associated with each page and destroy the main frame in order to
        have a clean screen to add new elements
        @param the instance, the page that need to be cleaned
        @return Nothing
        """
        # Clear the previous page content and the main frame in order to be sure that there is nothing left
        page.clear_page()
        self.main_frame.destroy()

    def create_new_main_frame(self):
        """!
        @brief This function creates a new empty frame that will contain the elements of a new page
        @param the instance
        @return Nothing
        """
        # Creation of a main frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
