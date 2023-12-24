import tkinter as tk
from tkinter import ttk

from tkinter.messagebox import *
from ttkthemes import ThemedTk, ThemedStyle
from view.new_observation_window import NewObservation
from view.login_as_admin_window import LoginAsAdministrator
from view.modify_or_create_configuration_window import ModifyOrCreateConfiguration
from view.summary_window import Summary
from view.selection_sensor_quantity_window import QuantitySensor
from view.labellisation_sensor_window import LabelisationSensor
from view.sensor_pairing_management_window import SensorPairingManagement


class App(ThemedTk):
    def __init__(self):
        ThemedTk.__init__(self)
        self.title("PRISM@Home")
        self.attributes('-fullscreen', True)
        self.bind('<Escape>', lambda e: self.attributes('-fullscreen', False))

        # Theme of the application
        self.style = ThemedStyle(self)
        self.style.set_theme("breeze")  # Write the theme you would like

        self.show_frame()

    def show_frame(self):
        # Création du cadre principal
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.call_new_observation()

    def call_new_observation(self):
        # Redirecting to the login page
        new_observation_page = NewObservation(self)
        new_observation_page.show_page()

        # Redirection to login as an admin button
        ttk.Button(self.main_frame, text="Login as administrator", command=lambda: self.redirect_to_login_as_admin(new_observation_page)).place(relx=0.9, rely=0.1)

        # Redirection to login as an admin button
        ttk.Button(new_observation_page.frame, text="Import configuration", command=lambda: self.redirect_to_pairing(new_observation_page)).pack()

    def redirect_to_login_as_admin(self, new_observation_page):

        # Clear the previous page content
        self.clear_the_page(new_observation_page)

        # Creation of a main frame
        self.create_new_main_frame()

        # Redirecting to the login page
        login_as_admin_page = LoginAsAdministrator(self.master)
        login_as_admin_page.show_page()

        # Connection button
        ttk.Button(login_as_admin_page.frame, text="Connexion", command=lambda: self.connexion_button_clic(login_as_admin_page)).pack(pady=20)

        # Cancel button to redirect to the new observation  page
        ttk.Button(self.main_frame, text="Cancel", command=lambda: self.redirect_to_new_observation(login_as_admin_page)).place(relx=0.9, rely=0.1)


    def connexion_button_clic(self, login_as_admin_page):
        login_value = login_as_admin_page.login_entry.get()
        password_value = login_as_admin_page.password_entry.get()

        # Print the chosen data
        print("Login :", login_value)
        print("Password :", password_value)

        if login_as_admin_page.connexion_admin() == False:
            showerror("Error", "The login or the password is incorrect")
        else:
            self.redirect_to_modify_or_create_configuration(login_as_admin_page)
            pass

    def redirect_to_new_observation(self, page):

        # Clear the previous page content
        self.clear_the_page(page)

        # Creation of a main frame
        self.create_new_main_frame()

        self.call_new_observation()

    def redirect_to_modify_or_create_configuration(self, page):

        # Clear the previous page content
        self.clear_the_page(page)

        # Creation of a main frame
        self.create_new_main_frame()

        modify_or_create_configuration_page = ModifyOrCreateConfiguration(self.master)
        modify_or_create_configuration_page.show_page()

        # Logout Button
        logout_button = ttk.Button(self.main_frame, text="Log out", command=lambda: self.redirect_to_new_observation(modify_or_create_configuration_page))
        logout_button.place(relx=0.9, rely=0.01)  # Position the logout button above the frames

        modify_button = ttk.Button(modify_or_create_configuration_page.left_frame, text="Modify the configuration",
                                   command=lambda: self.redirect_to_selection_sensor_quantity_from_create_a_config(modify_or_create_configuration_page))
        modify_button.pack(side="bottom", fill="x")

        # Create a new configuration button
        create_button = ttk.Button(modify_or_create_configuration_page.right_frame, text="Create a configuration",
                                  command=lambda: self.redirect_to_selection_sensor_quantity_from_create_a_config(modify_or_create_configuration_page))
        create_button.pack(side="bottom", fill="x")


    def redirect_to_selection_sensor_quantity_from_create_a_config(self, page):
        # Clear the previous page content
        page.on_create_configuration_button_click()

        # Clear the previous page content
        self.clear_the_page(page)

        selction_sensor_quantity_page = QuantitySensor(self)
        selction_sensor_quantity_page.show_page()

        # Creation of a main frame
        self.create_new_main_frame()

        # Add buttons
        back_button = ttk.Button(self.main_frame, text="Back", command=lambda: self.redirect_to_modify_or_create_configuration(selction_sensor_quantity_page))
        back_button.pack(side=tk.LEFT, padx=10, expand=True)

        next_button = ttk.Button(self.main_frame, text="Next", command=lambda: self.redirect_to_labellisation_sensor(selction_sensor_quantity_page))
        next_button.pack(side=tk.RIGHT, padx=10, expand=True)


    def redirect_to_selection_sensor_quantity(self, page):

        # Clear the previous page content
        self.clear_the_page(page)

        selction_sensor_quantity_page = QuantitySensor(self)
        selction_sensor_quantity_page.show_page()

        # Creation of a main frame
        self.create_new_main_frame()

        # Add buttons
        back_button = ttk.Button(self.main_frame, text="Back", command=lambda: self.redirect_to_modify_or_create_configuration(selction_sensor_quantity_page))
        back_button.pack(side=tk.LEFT, padx=10, expand=True)

        next_button = ttk.Button(self.main_frame, text="Next", command=lambda: self.redirect_to_labellisation_sensor(selction_sensor_quantity_page))
        next_button.pack(side=tk.RIGHT, padx=10, expand=True)


    def redirect_to_labellisation_sensor(self, page):

        page.on_next_button_click()
        # Clear the previous page content
        self.clear_the_page(page)

        labellisation_sensor_page = LabelisationSensor(self)
        labellisation_sensor_page.show_page()

        # Creation of a main frame
        self.create_new_main_frame()

        # Add buttons
        back_button = ttk.Button(self.main_frame, text="Back", command=lambda: self.redirect_to_selection_sensor_quantity(labellisation_sensor_page))
        back_button.pack(side=tk.LEFT, padx=10, expand=True)

        next_button = ttk.Button(self.main_frame, text="Next", command=lambda: self.redirect_to_summary_from_labellisation(labellisation_sensor_page))
        next_button.pack(side=tk.RIGHT, padx=10, expand=True)


    def redirect_to_summary_from_labellisation(self, page):
        # Clear the previous page content
        self.clear_the_page(page)

        # Creation of a main frame
        self.create_new_main_frame()

        summary_page = Summary(self)
        summary_page.show_page()

        # Cancel button
        concenl_button = ttk.Button(self.main_frame, text="Cancel", command=lambda: self.redirect_to_modify_or_create_configuration(summary_page))
        concenl_button.pack(side=tk.LEFT, padx=10, expand=True)

        # Back button
        back_button = ttk.Button(self.main_frame, text="Back", command=lambda: self.redirect_to_labellisation_sensor(summary_page))
        back_button.pack(side=tk.LEFT, padx=10, expand=True)

        # Validate configuration button
        back_button = ttk.Button(self.main_frame, text="Validate configuration", command=lambda: self.redirect_to_modify_or_create_configuration(summary_page))
        back_button.pack(side=tk.LEFT, padx=10, expand=True)


    def redirect_to_pairing(self, page):
        # Clear the previous page content
        self.clear_the_page(page)

        sensor_pairing_page = SensorPairingManagement(self)
        sensor_pairing_page.show_page()

        # Creation of a main frame
        self.create_new_main_frame()

        # Add buttons
        back_button = ttk.Button(self.main_frame, text="Back", command=lambda: self.redirect_to_new_observation(sensor_pairing_page))
        back_button.pack(side=tk.LEFT, padx=10, expand=True)

        # Rediraction to summary to confirm the configuration
        next_button = ttk.Button(self.main_frame, text="Next", command=lambda: self.redirect_to_summary_from_pairing(sensor_pairing_page))
        next_button.pack(side=tk.RIGHT, padx=10, expand=True)

    def redirect_to_summary_from_pairing(self, page):
        # Clear the previous page content
        self.clear_the_page(page)

        # Creation of a main frame
        self.create_new_main_frame()

        summary_page = Summary(self)
        summary_page.show_page()

        # Cancel button
        concenl_button = ttk.Button(self.main_frame, text="Exit", command=lambda: self.redirect_to_new_observation(summary_page))
        concenl_button.pack(side=tk.LEFT, padx=10, expand=True)

        # Back button
        back_button = ttk.Button(self.main_frame, text="Back", command=lambda: self.redirect_to_pairing(summary_page))
        back_button.pack(side=tk.LEFT, padx=10, expand=True)

        # Start observation button
        #back_button = ttk.Button(self.main_frame, text="Start observation", command=lambda: self.redirect_to_modify_or_create_configuration(summary_page))
        #back_button.pack(side=tk.LEFT, padx=10, expand=True)


    def clear_the_page(self, page):
        # Clear the previous page content and the main frame in order to be sure that there is nothing left
        page.clear_page()
        self.main_frame.destroy()

    def create_new_main_frame(self):
        # Creation of a main frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)



