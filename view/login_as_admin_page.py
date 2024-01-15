"""!
@file login_as_admin_page.py
@brief This file will contain all the widgets and functions related to the "login as admin" page itself
@author Naviis-Brain
@version 1.0
@date
"""
import tkinter as tk
from tkinter import ttk, messagebox

import mysql.connector
import globals
from model import local

from controller.entry_manager import EntryManager


class LoginAsAdministrator:
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
        @brief The show_page function creates and displays all the elements of the "login_as_admin" page
        @param self : the instance
        @return Nothing
        """
        self.frame = ttk.Frame(self.master)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Displays the title of the page
        label = ttk.Label(self.frame, text="Connexion Administrator", font=16)
        label.pack(pady=20)

        # login input
        login_label = ttk.Label(self.frame, text="Login")
        login_label.pack()
        self.login_entry = EntryManager(self.frame, min=1, max=30, has_width=30)

        # password input
        password_label = ttk.Label(self.frame, text="Password")
        password_label.pack()
        self.password_entry = EntryManager(self.frame, min=0, max=30, has_width=30, is_password=True,
                                           has_special_char=True)

        # Display the frame with all the elements
        self.frame.pack(fill=tk.BOTH, expand=True)

    def clear_page(self):
        """!
        @brief This functions clears the entire "new observation" page
        @param self : the instance
        @return Nothing
        """
        # Destroy the frame
        self.frame.destroy()

    def connexion_admin(self):
        """!
        @brief This functions collects the login and the password entered by the user and checks if they are correct.
        This function displays message according to the result of the connexion test
        @param self : the instance
        @return the boolean connexion_allowed that will return true if the connexion is allowed else false
        """
        username = self.login_entry.get()
        password = self.password_entry.get()
        globals.global_connected_admin_login = username
        globals.global_connected_admin_password = password

        connexion_allowed = False

        print(username)
        print(password)

        user = local.get_user_from_login_and_password(username, password)
        print(user)

        # Check if the user was found in the database
        if user:
            globals.global_id_user = user[0]
            local.update_user_connexion_status(user[0], 1)
            connexion_allowed = True
        else:
            messagebox.showerror("Connexion error", "Login or password incorrect")

        return connexion_allowed
