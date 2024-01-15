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

import globals
from model import local
from view.new_observation_page import NewObservation
from view.login_as_admin_page import LoginAsAdministrator
from view.modify_or_create_configuration_page import ModifyOrCreateConfiguration
from view.summary_admin_page import SummaryAdmin
from view.summary_user_page import SummaryUser
from view.selection_sensor_quantity_page import QuantitySensor
from view.labellisation_sensor_page import LabelisationSensor
from view.sensor_pairing_management_page import SensorPairingManagement
import webbrowser
import sys
from model import local
# from model import remote
import globals


class App(ThemedTk):

    def __init__(self):
        """!
        @brief The __init__ function creates and set the theme and parameter of the window that will contain the pages of the
        user interface
        @param self : the instance
        @return Nothing
        """
        ThemedTk.__init__(self)
        self.title("PRISM@Home")

        my_os = sys.platform

        if my_os == 'Linux':
            self.attributes('-zoomed', True)
            self.bind('<Escape>', lambda e: self.attributes('-zoomed', False))
        elif my_os == 'win32' or my_os == 'cygwin':
            self.attributes('-fullscreen', True)
            self.bind('<Escape>', lambda e: self.attributes('-fullscreen', False))

        # Theme of the application
        self.style = ThemedStyle(self)
        self.style.set_theme("breeze")  # Write the theme you would like

        # Protool incas of closing window
        self.protocol("WM_DELETE_WINDOW", self.closing_protocol)

        # Creating main frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.is_observation_running()

    def is_observation_running(self):
        """!
        @brief This function checks if an observation is running and depending on the result will either redirect the
        user to the new observation page (no observation is running) or the summary user page (an observation is running)
        @param self : the instance
        @return Nothing
        """
        globals.global_new_id_observation = local.get_active_observation()
        if globals.global_new_id_observation == None:
            self.call_new_observation_page()
        else:
            self.call_summary_user_page()

    def call_new_observation_page(self):
        """!
        @brief This function initialises and calls new_observation_page.py in order to show the page and also adds
        navigation button
        @param self : the instance
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
                   command=lambda: self.is_a_config_chosen(new_observation_page)).pack()

    def call_summary_user_page(self):
        """!
        @brief This function initialises and calls summary_user.py in order to show the page and also adds
        navigation button
        @param self : the instance
        @return Nothing
        """
        # Redirecting to the login page
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
                                 command=lambda: self.redirect_to_pairing_from_anywhere(summary_user_page))
        back_button.pack(side=tk.LEFT, padx=10, expand=True)

        # Start observation button
        button = ttk.Button(self.main_frame, text="Stop observation")
        button.config(command=lambda: self.stop_observation(button, summary_user_page))
        button.pack(side=tk.LEFT, padx=10, expand=True)

    def redirect_to_new_observation_from_anywhere(self, page):
        """!
        @brief This function clears the previous page before calling the new observation page
        @param self : the instance
        @param page : the previous page
        @return Nothing
        """
        # Clear the previous page content
        self.clear_the_page(page)

        # Creation of a main frame
        self.create_new_main_frame()

        self.call_new_observation_page()

    def redirect_to_new_observation_from_modify_or_create_a_config(self, modify_or_create_configuration_page):
        """!
        @brief This function logs the admins out before redirecting to the nex observation page
        @param self : the instance
        @param modify_or_create_configuration_page : the "modify or create a config" page
        @return Nothing
        """
        # Logging out the admin
        local.update_user_connexion_status(globals.global_id_user, 0)

        # Redirecting to the new observation page
        self.redirect_to_new_observation_from_anywhere(modify_or_create_configuration_page)

    def is_a_config_chosen(self, new_observation_page):
        """!
        @brief This function checks that the user has chosen a configuration for the observation. If no configuration
        was chosen, an error pop up is displayed, else the user can access the pairing page
        @param self : the instance
        @param new_observation_page : the previous page
        @return Nothing
        """
        if new_observation_page.configuration_combobox.get() == "":
            messagebox.showerror("Error", "Please select a configuration.")
        elif new_observation_page.configuration_combobox.get() == "No configuration available":
            messagebox.showerror("Error", "Please create or import a configuration to start the observation.")
        else:
            new_observation_page.on_import_button_click()
            self.redirect_to_pairing_from_anywhere(new_observation_page)

    def redirect_to_pairing_from_anywhere(self, page):
        """!
        @brief This function clears the previous page in order to display the content of the pairing page and adds
        navigation buttons to the page
        @param self : the instance
        @param page : the previous page
        @return Nothing
        """
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
        next_button = ttk.Button(self.main_frame, text="Validate",
                                 command=lambda: self.redirect_to_summary_user_from_pairing(sensor_pairing_page))
        next_button.pack(side=tk.RIGHT, padx=10, expand=True)

    def redirect_to_login_as_admin_from_anywhere(self, page):
        """!
        @brief This function clears the new observation page in order to display the content of the the login as admin page
        and adds navigations buttons to the page
        @param self : the instance
        @param page : the previous page
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
            relx=0.9, rely=0.1)

    def connexion_button_clic(self, login_as_admin_page):
        """!
        @brief This function calls the connexion_admin function located in the "login as admin page" in order to check
        if the login and password entered by the user are correct
        @param self : the instance
        @param login_as_admin_page : the login as admin page
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
        @param self : the instance
        @param page : the previous page
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
                                   command=lambda: self.redirect_to_new_observation_from_modify_or_create_a_config(
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
        then calls the function that display the "modify or create a configuration" page
        @param self : the instance
        @param summary_admin_page : the summary admin page
        @return Nothing
        """
        # Log the data into the database
        summary_admin_page.validate_conf()

        # Go back to the "modify or create a configuration page"
        self.redirect_to_modify_or_create_configuration_from_anywhere(summary_admin_page)

    def redirect_to_selection_sensor_quantity_from_create_a_config(self, modify_or_create_a_config_page):
        """!
        @brief This function first checks if the label of the config chosen by the user is not already taken. In that
        case, it will display an error message asking the user to choose another name for the configuration.
        If the name doesn't already exist, the function allows the inputs of the user to be saved locally and then calls
        the redirection to the "selection sensor quantity" page
        @param self: the instance
        @param modify_or_create_a_config_page : the create or modify a configuration page
        @return Nothing
        """

        # Checks if the user has chosen a unique name for the configuration
        label = modify_or_create_a_config_page.name_entry.get()
        print("config label = ", label)
        if local.config_label_exists(label):
            # Display a message asking the user to choose another name
            messagebox.showerror("Error", "This configuration name already exists. Please choose another one.")
        else:
            # Create a new configuration in the database
            modify_or_create_a_config_page.save_label_description_id_of_config_into_globals()

            # Redirection to the "selection sensor quantity" page
            self.redirect_to_selection_sensor_quantity_from_anywhere(modify_or_create_a_config_page)

    def redirect_to_selection_sensor_quantity_from_anywhere(self, page):
        """!
        @brief This function clears the previous page in order to display the content of the "selection sensor quantity"
        page and adds navigations buttons.
        @param self : the instance
        @param page : the previous page
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
        @param self : the instance
        @param selection_sensor_quantity_page : the selection_sensor_quantity_page
        @return Nothing
        """
        if selection_sensor_quantity_page.chose_at_least_one_sensor():
            # Calls this function in order to store into global variables the datas entered by the user in the sensor
            # quantity page
            selection_sensor_quantity_page.save_sensors_quantity_into_globals()
            self.redirect_to_labellisation_sensor_from_anywhere(selection_sensor_quantity_page)
        else:
            messagebox.showerror("Error", "Please select at least one sensor")

    def redirect_to_labellisation_sensor_from_anywhere(self, page):
        """!
        @brief This function clears the previous page in order to display the content of the "labellisation sensor"
        page and adds navigations buttons. It also allows to save into global variables the data entered by the user in the
        previous page
        @param self : the instance
        @param page : the selection sensor quantity page
        @return Nothing
        """
        # Clear the previous page content
        self.clear_the_page(page)

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
                                 command=lambda: self.redirect_to_summary_admin_from_labellisation(
                                     labellisation_sensor_page))
        next_button.pack(side=tk.RIGHT, padx=10, expand=True)

    def redirect_to_summary_admin_from_labellisation(self, labellisation_sensor_page):
        """!
        @brief This function clears the previous page in order to display the content of the "summary admin"
        page and adds navigations buttons. It also saves the data in the "labellisation" page
        entered by the user into global variables
        @param self : the instance
        @param labellisation_sensor_page : the labellisation page
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
        cancel_button = ttk.Button(self.main_frame, text="Cancel",
                                   command=lambda: self.redirect_to_modify_or_create_configuration_from_anywhere(
                                       summary_admin_page))
        cancel_button.pack(side=tk.LEFT, padx=10, expand=True)

        # Back button
        back_button = ttk.Button(self.main_frame, text="Back",
                                 command=lambda: self.redirect_to_labellisation_sensor_from_anywhere(
                                     summary_admin_page))
        back_button.pack(side=tk.LEFT, padx=10, expand=True)

        # Validate configuration button
        back_button = ttk.Button(self.main_frame, text="Validate configuration",
                                 command=lambda: self.redirect_to_modify_or_create_configuration_after_config_validation
                                 (summary_admin_page))
        back_button.pack(side=tk.LEFT, padx=10, expand=True)

    def redirect_to_summary_user_from_pairing(self, sensor_pairing_page):
        """!
        @brief This function saves the information about the pairing of the sensor and calls the 'Summary user' page
        @param self : the instance
        @param sensor_pairing_page : the sensor pairing page
        @return Nothing
        """
        # Saving the infos about the pairing
        sensor_pairing_page.on_validate_button_click()

        # Redirecting to the 'Summary user' page
        self.redirect_to_summary_user_from_anywhere(sensor_pairing_page)

    def redirect_to_summary_user_from_anywhere(self, page):
        """!
        @brief This function clears the previous page in order to display the content of the "summary user"
        page and adds navigations buttons.
        @param self : the instance
        @param page : the previous page
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
                                 command=lambda: self.redirect_to_pairing_from_anywhere(summary_user_page))
        back_button.pack(side=tk.LEFT, padx=10, expand=True)

        # Start observation button
        button = ttk.Button(self.main_frame, text="Start observation")
        button.config(command=lambda: self.start_observation(button, summary_user_page))
        button.pack(side=tk.LEFT, padx=10, expand=True)

    def start_observation(self, button, summary_user_page):
        """!
        @brief This function starts the observation and change the label of the button
        @param self : the instance
        @param button : the start observation button
        @:param summary_user_page : the summary user page
        @return Nothing
        """

        # Calling the function to start the observation
        local.update_observation_status()

        messagebox.showinfo("Start observation", "The observation is started.")

        # Changing the label and the function associated to the button
        button.config(text="Stop observation", command=lambda: self.stop_observation(button, summary_user_page))

    def stop_observation(self, button, summary_user_page):
        """!
        @brief This function allows the user to stop the observation and change the label of the button
        @param self : the instance
        @param button : the stop observation button
        @:param summary_user_page : the summary user page
        @return Nothing
        """

        # Calling the function to stop the observation
        # TODO Mathilde : voir où appeller la fonction car lorsque que je la met au bonne endroit ca pose probleme
        #  + voir avec les indus comment stopper la reception des datas
        local.update_observation_status(0)

        messagebox.showinfo("Stop observation", "The observation is stopped.")

        # Changing the label and the function associated to the button
        button.config(text="Start observation", command=lambda: self.start_observation(button, summary_user_page))

    def clear_the_page(self, page):
        """!
        @brief This function calls the clear page function associated with each page and destroy the main frame in order to
        have a clean screen to add new elements
        @param self : the instance
        @param page : the page that need to be cleared
        @return Nothing
        """
        # Clear the previous page content and the main frame in order to be sure that there is nothing left
        page.clear_page()
        self.main_frame.destroy()

    def create_new_main_frame(self):

        """!
        @brief This function creates a new empty frame that will contain the elements of a new page
        @param self : the instance
        @return Nothing
        """
        # Creation of a main frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

    def closing_protocol(self):
        """!
        @brief This function deals with the closing of the app
        @param self : the instance
        @return Nothing
        """
        if messagebox.askokcancel("Quit", "Are you sure you want to quit PRISM@Home ?"):
            globals.thread_done = True
            if globals.global_connected_admin_login is not None:
                print("Deconnexion normalement")
                local.update_user_connexion_status(globals.global_connected_admin_login, globals.global_connected_admin_password, 0)
            self.destroy()
