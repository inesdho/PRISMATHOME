"""!
@file update_local_database.py
@brief This file will contain all the functions allowing the App to fetch data for the remote database into the
local database
@author Naviis-Brain
@version 1.0
@date 31st January 2024
"""
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from model import remote
import mysql.connector


class FunctionSelectionDialog(tk.Toplevel):
    """!
    @brief This class displays a pop-up asking the user which data they would like to update in the local database,
    teh functions of data fetching will be called depending on the answers
    @param self : the instance
    @return Nothing
    """

    def __init__(self, callback):
        """!
        @brief This function displays the pop-up and its content.
        @param self : the instance
        @param callback : The callback function to handle the selected function.
        @return Nothing
        """
        super().__init__()

        self.title("Import data")
        self.selection_var = tk.StringVar()

        ttk.Label(self, text="Which data would you like to import :").pack(pady=10)

        functions = ["User", "Configuration"]

        self.listbox = tk.Listbox(self, selectmode=tk.MULTIPLE)
        for function in functions:
            self.listbox.insert(tk.END, function)
        self.listbox.pack(pady=10)

        ttk.Button(self, text="OK", command=self.on_ok).pack(pady=10)

        self.callback = callback

    def on_ok(self):
        """!
        @brief This function saves the results and destroy the pop-up
        @param self : the instance
        @return Nothing
        """
        selected_functions = [self.listbox.get(idx) for idx in self.listbox.curselection()]
        self.callback(selected_functions)
        self.destroy()


class UpdateLocalDatabase:
    """!
    @brief This class calls the functions related to the pop-up and execute the functions allowing the user to update
    the local database using the data from the remote database.
    @return Nothing
    """

    def __init__(self):
        self.show_function_selection_dialog()

    def show_function_selection_dialog(self):
        """!
        @brief This functions calls the FunctionSelectionDialog in order to create the pop-up
        @param self : The instance
        @return Nothing
        """

        # Callback to handle the function selection
        def handle_function_selection(selected_functions):
            self.run_selected_functions(selected_functions)

        # Calling the pop-up
        dialog = FunctionSelectionDialog(handle_function_selection)
        # Keep showing the pop-up
        dialog.mainloop()

    def run_selected_functions(self, selected_functions):
        """!
        @brief This functions calls the FunctionSelectionDialog in order to create the pop-up
        @param self : The instance
        @param selected_functions : The functions selected by the user in order to be run
        @return Nothing
        """
        if selected_functions is None:
            return

        get_users = 0
        get_configs = 0
        if 'Configuration' in selected_functions:
            get_configs = 1
            get_users = 1   # If you want to get configs, you also need to get all users for FK constraints
        elif 'User' in selected_functions:
            get_users = 1

        result = remote.fetch_remote_configs(get_users, get_configs)

        if result == 1:
            messagebox.showinfo("Import complete", "The import of selected data was successful.")
        else:
            messagebox.showinfo("IMPORT ERROR", "Import failed.")
