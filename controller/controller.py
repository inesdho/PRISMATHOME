"""!
@file controller.py
@brief This file will contain all the redirection between the pages of the user and admin interface
@author Naviis-Brain
@version 1.0
@date
"""
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess

from ttkthemes import ThemedTk, ThemedStyle

from utils import globals
from model import local
from view.new_observation_page import NewObservation
from view.login_as_admin_page import LoginAsAdministrator
from view.modify_or_create_configuration_page import ModifyOrCreateConfiguration
from view.summary_admin_page import SummaryAdmin
from view.summary_user_page import SummaryUser
from view.selection_sensor_quantity_page import QuantitySensor
from view.labellisation_sensor_page import LabelisationSensor
from view.sensor_pairing_management_page import SensorPairingManagement
from utils import system_function
import sys
import signal


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

        if my_os == 'Linux' or my_os == 'linuxarm':
            self.attributes('-zoomed', True)
            self.bind('<Escape>', lambda e: self.attributes('-zoomed', False))
        elif my_os == 'win32' or my_os == 'cygwin':
            self.attributes('-fullscreen', True)
            self.bind('<Escape>', lambda e: self.attributes('-fullscreen', False))

        self.lift()

        # Theme of the application
        self.style = ThemedStyle(self)
        self.style.set_theme("breeze")  # Write the theme you would like

        # Protool incas of closing window
        self.protocol("WM_DELETE_WINDOW", self.closing_protocol)

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
        # Creation of a main frame
        self.create_new_main_frame()

        # Redirecting to the login page
        new_observation_page = NewObservation(self)
        new_observation_page.show_page()

        # Redirection to login as an admin button
        ttk.Button(self.main_frame, text="Login as administrator",
                   command=lambda: self.redirect_to_login_as_admin_from_anywhere(new_observation_page)) \
            .pack(side=tk.RIGHT, padx=10, anchor='e')

        # Export local data
        button_get_data = ttk.Button(self.main_frame, text="Export local data to file", command=lambda: self.get_data())
        button_get_data.pack(side=tk.RIGHT, padx=10, anchor='e')

        # Redirection to login as an admin button
        ttk.Button(new_observation_page.frame, text="Import configuration",
                   command=lambda: self.redirect_to_pairing_from_new_observation(new_observation_page)).pack(pady=10)


    def call_summary_user_page(self):
        """!
        @brief This function initialises and calls summary_user.py in order to show the page and also adds
        navigation button. This function is used to display the page specifically when the app is launch and an
        observation is already running
        @param self : the instance
        @return Nothing
        """
        # Redirecting to the login page
        summary_user_page = SummaryUser(self)
        summary_user_page.show_page()

        # Creation of a main frame
        self.create_new_main_frame()

        # Update the state of the observation
        summary_user_page.observation_state.config(text="Observation running", foreground='#3eaf3e')

        # Cancel button
        cancel_button = ttk.Button(self.main_frame, text="Cancel",
                                   command=lambda: self.redirect_to_new_observation_from_summary_user(summary_user_page))
        cancel_button.pack(side=tk.LEFT, padx=10, expand=True)

        # Start observation button
        button = ttk.Button(self.main_frame, text="Stop observation")
        button.config(command=lambda: self.stop_observation(button, summary_user_page))
        button.pack(side=tk.LEFT, padx=10, expand=True)

        # Export local data to file button
        button_get_data = ttk.Button(self.main_frame, text="Export local data to file", command=lambda: self.get_data())
        button_get_data.pack(side=tk.LEFT, padx=10, expand=True)

    def redirect_to_new_observation_from_anywhere(self, page):
        """!
        @brief This function clears the previous page before calling the new observation page
        @param self : the instance
        @param page : the previous page
        @return Nothing
        """
        # Clear the previous page content
        self.clear_the_page(page)

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

    def redirect_to_pairing_from_new_observation(self, new_observation_page):
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
        elif new_observation_page.participant_entry.get() == "" or new_observation_page.session_entry.get() == "":
            messagebox.showerror("Error", "Please fill all the field before continuing.")
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
        login_as_admin_page = LoginAsAdministrator(self)
        login_as_admin_page.show_page()

        # Connection button
        ttk.Button(login_as_admin_page.frame, text="Connexion",
                   command=lambda: self.connexion_button_clic(login_as_admin_page)).pack(pady=20)

        # Cancel button to redirect to the new observation page
        ttk.Button(self.main_frame, text="Cancel",
                   command=lambda: self.redirect_to_new_observation_from_anywhere(login_as_admin_page)) \
            .pack(side=tk.TOP, padx=10, expand=True, anchor='e')

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

        # Set the 'is modification' value to False
        globals.global_is_modification = False
        globals.sensor_counts.clear()
        globals.global_sensor_entries.clear()

        # Creation of the "modify or create configuration page"
        modify_or_create_configuration_page = ModifyOrCreateConfiguration(self)
        modify_or_create_configuration_page.show_page()

        # Logout Button
        ttk.Button(self.main_frame, text="Log out",
                   command=lambda: self.redirect_to_new_observation_from_modify_or_create_a_config(
                       modify_or_create_configuration_page)).place(relx=0.9, rely=0.1)

        # Modify Button
        modify_button = ttk.Button(modify_or_create_configuration_page.left_frame, text="Modify the configuration",
                                   command=lambda: self.redirect_to_selection_sensor_quantity_to_modify_a_config(
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
        if globals.global_is_modification:
            summary_admin_page.validate_conf_for_modify()
        else:
            # Log the data into the database
            summary_admin_page.validate_conf_for_create()

        # Go back to the "modify or create a configuration page"
        self.redirect_to_modify_or_create_configuration_from_anywhere(summary_admin_page)

    def redirect_to_selection_sensor_quantity_to_modify_a_config(self, modify_or_create_configuration_page):
        """!
        @brief This function update the global variable indicating if this is a "modify a configuration" context to True
        and redirect to the 'selection sensor quantity' page
        @param self : the instance
        @param modify_or_create_configuration_page : the modify_or_create_configuration_page
        @return Nothing
        """
        if modify_or_create_configuration_page.configuration_combobox.get() == 'No configuration available':
            messagebox.showerror("Error", "No observation exist locally, please create or import one to be able to use the modify function.")
        else:
            modify_or_create_configuration_page.start_config_modification()
            # Set the modification indicator to True
            globals.global_is_modification = True
            # Redirection to selection sensor quantity
            self.redirect_to_selection_sensor_quantity_from_anywhere(modify_or_create_configuration_page)

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
        label = modify_or_create_a_config_page.configuration_label_entry.get()
        description = modify_or_create_a_config_page.configuration_description_text.get()

        # Checks if the user has filled the label and the description
        if label == "" or description == "":
            messagebox.showerror("Error", "The label and the description must be filled.")
        # Checks if the user has chosen a unique name for the configuration
        elif local.config_label_exists(label):
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
        back_button = ttk.Button(self.main_frame, text="Cancel",
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
            messagebox.showerror("Error", "Please select at least one sensor.")

    def redirect_to_selection_sensor_quantity_from_labellisation(self, labellisation_sensor_page):
        """!
        @brief This function saves the label that the user entrerd before redirecting him to selection sensor quantity
        @param self : the instance
        @param labellisation_sensor_page : the labellisation page
        @return Nothing
        """

        # Saves the data entered by the user in the labellisation page into global variables
        labellisation_sensor_page.get_sensor_data()
        # Redirect to the summary admin page
        self.redirect_to_selection_sensor_quantity_from_anywhere(labellisation_sensor_page)

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
        cancel_button = ttk.Button(self.main_frame, text="Back",
                                   command=lambda: self.redirect_to_selection_sensor_quantity_from_labellisation(
                                       labellisation_sensor_page))
        cancel_button.pack(side=tk.LEFT, padx=10, expand=True)

        next_button = ttk.Button(self.main_frame, text="Next",
                                 command=lambda: self.redirect_to_summary_admin_from_labellisation(
                                     labellisation_sensor_page))
        next_button.pack(side=tk.RIGHT, padx=10, expand=True)

    def redirect_to_summary_admin_from_labellisation(self, labellisation_sensor_page):
        """!
        @brief This function checks that all the datas that the user have to fill are filled and all the labels are
        unique. If so the function saves the data in the "labellisation" page then redirect to the summary admin page.
        If not an error message is displayed.
        entered by the user into global variables
        @param self : the instance
        @param labellisation_sensor_page : the labellisation page
        @return Nothing
        """

        if labellisation_sensor_page.are_all_field_filled():
            if labellisation_sensor_page.are_all_label_unique():
                if labellisation_sensor_page.are_label_not_only_numbers():
                    # Saves the data entered by the user in the labellisation page into global variables
                    labellisation_sensor_page.get_sensor_data()
                    # Redirect to the summary adminpage
                    self.redirect_to_summary_admin_from_anywhere(labellisation_sensor_page)
                else:
                    messagebox.showerror("Error", "Labels can't be only number.")
            else:
                messagebox.showerror("Error", "All the label must be unique.")
        else:
            messagebox.showerror("Error", "Please fill all the label and descriptions.")

    def redirect_to_summary_admin_from_anywhere(self, page):
        """!
        @brief This function clears the previous page in order to display the content of the "summary admin"
        page and adds navigations buttons.
        @param self : the instance
        @param page : the previous page
        @return Nothing
        """
        # Clear the previous page content
        self.clear_the_page(page)

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
        @brief This function asks the user if they want to anable the local only mode.
        It saves the information about the pairing of the sensor and calls the 'Summary user' page
        @param self : the instance
        @param sensor_pairing_page : the sensor pairing page
        @return Nothing
        """
        only_local = messagebox.askyesno("Mode local only",
                                     "You are about to start an observation. Do you want to activate the local only mode ?")

        # Saving the infos about the pairing
        sensor_pairing_page.on_validate_button_click(only_local)

        # Redirecting to the 'Summary user' page
        self.redirect_to_summary_user_from_anywhere(sensor_pairing_page)

    def redirect_to_new_observation_from_summary_user(self, summary_user_page):
        """!
        @brief This function asks the user if they want to exit the observation because there will be no going back.
        @param self : the instance
        @param page : the previous page
        @return Nothing
        """
        if messagebox.askyesno("End observation", "Are you sure you want to end the observation ? The observation cannot"
                                                  " be restarted. "):
            self.redirect_to_new_observation_from_anywhere(summary_user_page)

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

        # Update the state of the observation
        summary_user_page.observation_state.config(text="Observation not running", foreground='#d9534f')

        # Cancel button
        cancel_button = ttk.Button(self.main_frame, text="Cancel",
                                   command=lambda: self.redirect_to_new_observation_from_summary_user(summary_user_page))
        cancel_button.pack(side=tk.LEFT, padx=10, expand=True)

        # Start observation button
        start_stop_button = ttk.Button(self.main_frame, text="Start observation")
        start_stop_button.config(command=lambda: self.start_observation(start_stop_button, summary_user_page))
        start_stop_button.pack(side=tk.LEFT, padx=10, expand=True)

        # Export local data to file button
        button_get_data = ttk.Button(self.main_frame, text="Export local data to file", command=lambda: self.get_data())
        button_get_data.pack(side=tk.LEFT, padx=10, expand=True)

    def start_observation(self, start_stop_button, summary_user_page):
        """!
        @brief This function starts the observation and change the label of the button, it also adds a button to get
        the data from the DB
        @param self : the instance
        @param start_stop_button : the start observation button
        @param summary_user_page : the summary user page
        @return Nothing
        """

        # Update the state of the observation
        summary_user_page.observation_state.config(text="Observation running", foreground='#3eaf3e')

        # The list of sensors formated like "type/label"
        arguments = []

        # Get the sensor list from db
        sensor_list = local.get_sensors_from_observation(globals.global_new_id_observation)

        # Format the sensor list like "type/label" to start the program
        for sensor in sensor_list:
            arguments.append(sensor["type"] + "/" + sensor["label"])

        # Create the command
        command = ["python", "/home/share/PRISMATHOME/reception.py"] + arguments

        # Start the reception.py program
        subprocess.Popen(command)

        # Update observation status to start (1) in db
        local.update_observation_status(1)

        # Display a message that observation as started
        messagebox.showinfo("Start observation", "The observation is started.")

        # Changing the label and the function associated to the button
        start_stop_button.config(text="Stop observation", command=lambda: self.stop_observation(start_stop_button, summary_user_page))

    def stop_observation(self, start_stop_button, summary_user_page):
        """!
        @brief This function allows the user to stop the observation and change the label of the button
        @param self : the instance
        @param start_stop_button : the stop observation button
        @param summary_user_page : the summary user page
        @return Nothing
        """

        # Update the state of the observation
        summary_user_page.observation_state.config(text="Observation not running", foreground='#d9534f')

        # Get the program pid of reception.py
        program_pid = system_function.get_pid_of_script("reception.py")

        # Send a signal SIUSR1 to reception.py to stop it
        system_function.send_signal(program_pid, signal.SIGUSR1)

        # Update observation status to stop (0) in db
        local.update_observation_status(0)

        # Display a message that observation as stopped
        messagebox.showinfo("Stop observation", "The observation is stopped.")

        # Changing the label and the function associated to the button
        start_stop_button.config(text="Start observation", command=lambda: self.start_observation(start_stop_button, summary_user_page))

    def get_data(self):
        """!
        @brief This function asks the user to choose a path to save the queries
        @param self : the instance
        @return Nothing
        """
        # Creating Default Filename
        default_filename = "DATA"
        sys_id = local.get_system_id()
        if sys_id is not None:
            default_filename += "_syst" + str(sys_id)

        # Configuring file selection / creation window
        filetypes = [('SQL Files', '*.sql'), ('All Files', '*.*')]
        file_path = filedialog.asksaveasfilename(initialdir='/media', defaultextension='.sql', filetypes=filetypes,
                                                 confirmoverwrite=True, initialfile=default_filename)
        # If a path is returned by the window
        if file_path:
            directory, filename = os.path.split(file_path)
            if len(filename) > 0:   # Check if a filename was specified or only a directory was chosen
                queries = local.get_remote_queries()
                result = system_function.export_remote_queries(file_path, queries)
                if result is not False:
                    messagebox.showinfo("Data saved", f"Data successfully exported to {file_path}")
                else:
                    messagebox.showerror("Error", "Error ")
            else :
                messagebox.showerror("Error", "You have selected a directory, please select a file or specify the "
                                              "file name to create")
        else:
            messagebox.showerror("Error", "No path selected")

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
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5)

    def closing_protocol(self):
        """!
        @brief This function deals with the closing of the app
        @param self : the instance
        @return Nothing
        """
        # Display a confirmation popup before closing the app
        if messagebox.askokcancel("Quit", "Are you sure you want to quit PRISM@Home ?"):

            # Close the threads get_sensor_value
            globals.thread_done = True
            # Stop the functions local.connect_to_remote_db and local.connect_to_local_db if they are running
            globals.global_disconnect_request = True

            # Disconnect admin if connected
            if globals.global_id_user is not None:
                local.update_user_connexion_status(globals.global_id_user, 0)

            self.destroy()
