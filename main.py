import tkinter as tk
from tkinter import ttk

from vue.login_as_admin_window import LoginAsAdministrator
from vue.new_observation_window import NewObservation
from vue.selection_sensor_quantity_window import QuantitySensor


class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("PRISM@Home")
        self.attributes('-fullscreen', True)
        self.bind('<Escape>', lambda e: self.attributes('-fullscreen', False))

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
        redirect_button = ttk.Button(self.main_frame, text="Login as administrator", command= lambda : self.redirect_to_login_as_admin(new_observation_page))
        redirect_button.pack(side=tk.TOP, anchor=tk.NE, padx=10, pady=10)

        redirect_quantity_sensor_button = ttk.Button(self.main_frame, text="Quantity sensor", command= lambda : self.redirect_to_selection_sensor_quantity_window(new_observation_page))
        redirect_quantity_sensor_button.pack(side=tk.TOP, anchor=tk.NE, padx=10, pady=10)

    def redirect_to_login_as_admin(self, new_observation_page):
        # Clear the new_observation_window content
        new_observation_page.clear_page()
        self.main_frame.destroy()

        # Création du cadre principal
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Redirecting to the login page
        login_as_admin_page = LoginAsAdministrator(self.master)
        login_as_admin_page.show_page()

        # Redirection to login as an admin button
        redirect_button = ttk.Button(self.main_frame, text="Cancel", command=lambda: self.redirect_to_new_observation(login_as_admin_page))
        redirect_button.pack(side=tk.TOP, anchor=tk.NE, padx=10, pady=10)

    def redirect_to_new_observation(self, login_as_admin_page):
        # Clear the new_observation_window content
        login_as_admin_page.clear_page()
        self.main_frame.destroy()

        # Création du cadre principal
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.call_new_observation()


    def redirect_to_selection_sensor_quantity_window(self, new_observation_page):
        # Clear the new_observation_window content
        new_observation_page.clear_page()
        self.main_frame.destroy()

        # Création du cadre principal
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Redirecting to the login page
        quantity_page = QuantitySensor(self.master)
        quantity_page.show_page()



if __name__ == "__main__":
    app = App()
    app.mainloop()
