import tkinter as tk
from tkinter import ttk

from tkinter.messagebox import *
from ttkthemes import ThemedTk, ThemedStyle
from vue.new_observation_window import NewObservation
from vue.login_as_admin_window import LoginAsAdministrator
from vue.modify_or_create_configuration_window import ModifyOrCreateConfiguration
from vue.summary_window import Summary


class App(ThemedTk):
    def __init__(self):
        ThemedTk.__init__(self)
        self.title("PRISM@Home")
        self.attributes('-fullscreen', True)
        self.bind('<Escape>', lambda e: self.attributes('-fullscreen', False))

        # Configure le thème de l'application
        self.style = ThemedStyle(self)
        self.style.set_theme("breeze")  # Choisissez le thème que vous préférez

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


        # A SUPPRIMER bouton de redirection test vers la page summary
        ttk.Button(self.main_frame, text="TEST : accès page summary", command=lambda: self.redirect_to_summary(new_observation_page)).place(relx=0.5, rely=0.1)

        # TODO bouton vers la mise en place des capteurs une fois la config choisie

    def redirect_to_login_as_admin(self, new_observation_page):
        # Clear the new_observation_window content
        new_observation_page.clear_page()
        self.main_frame.destroy()

        # Creation of a main frame which will contain the button
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Redirecting to the login page
        login_as_admin_page = LoginAsAdministrator(self.master)
        login_as_admin_page.show_page()

        # Connection button
        ttk.Button(login_as_admin_page.frame, text="Connexion", command=lambda: self.connexion_button_clic(login_as_admin_page)).pack(pady=20)

        # Cancel button to redirect to the new observation  page
        ttk.Button(self.main_frame, text="Cancel", command=lambda: self.redirect_to_new_observation(login_as_admin_page)).place(relx=0.9, rely=0.1)

    # Get the data from the user input
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
        # Clear the login_as_admin_page content
        page.clear_page()
        self.main_frame.destroy()

        # Creation of a main frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.call_new_observation()

    def redirect_to_modify_or_create_configuration(self, login_as_admin_page):
        print("redirect_to_modify_or_create_configuration")
        # Clear the login_as_admin_page content
        login_as_admin_page.clear_page()
        print("clear page")

        self.main_frame.destroy()

        # Creation of a main frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        modify_or_create_configuration_page = ModifyOrCreateConfiguration(self.master)
        modify_or_create_configuration_page.show_page()

        # Logout Button
        logout_button = tk.Button(self.master, text="Log out", command=lambda: self.redirect_to_new_observation(modify_or_create_configuration_page))
        logout_button.place(relx=0.9, rely=0.01)  # Position the logout button above the frames


    def redirect_to_summary(self, page):
        # Clear the login_as_admin_page content
        page.clear_page()
        self.main_frame.destroy()

        # Creation of a main frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        summary_page = Summary(self)
        summary_page.show_page()

        # Cancel button to redirect to the new observation  page
        ttk.Button(self.main_frame, text="Cancel", command=lambda: self.redirect_to_new_observation(summary_page)).place(relx=0.9, rely=0.1)


if __name__ == "__main__":
    app = App()
    app.mainloop()
