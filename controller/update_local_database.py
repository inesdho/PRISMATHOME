"""!
@file update_local_database.py
@brief This file will contain all the functions allowing the App to fetch data for the remote database into the
local database
@author Naviis-Brain
@version 1.0
@date
"""
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import mysql.connector


# TODO remplacer les informations de connexion pour qu'elles correspondent aux bases locales et distantes
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

        functions = ["User", "Sensor type", "Configuration"]

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
        for selected_function in selected_functions:
            if selected_function == "User":
                try:
                    self.import_user_from_remote_to_local()
                except mysql.connector.Error as mysql_err:
                    # Raise the MySQL error to be caught in the main application
                    raise mysql_err
                except Exception as other_err:
                    # Raise other exceptions to be caught in the main application
                    raise other_err
            elif selected_function == "Sensor type":
                try:
                    self.import_sensor_type_from_remote_to_local()
                except mysql.connector.Error as mysql_err:
                    # Raise the MySQL error to be caught in the main application
                    raise mysql_err
                except Exception as other_err:
                    # Raise other exceptions to be caught in the main application
                    raise other_err
            elif selected_function == "Configuration":
                try:
                    self.import_config_from_remote_to_local()
                except mysql.connector.Error as mysql_err:
                    # Raise the MySQL error to be caught in the main application
                    raise mysql_err
                except Exception as other_err:
                    # Raise other exceptions to be caught in the main application
                    raise other_err

    def import_user_from_remote_to_local(self):
        """!
        @brief This function connects to the remote and local database and fetch the users from the remote
        database that doesn't appear in the local database and copy them locally
        @param self : the instance
        @return Nothing
        """
        try:
            # Connexion to remote database
            remote_conn = mysql.connector.connect(
                host="127.0.0.1",
                user="root",
                password="Q3fhllj2",
                database="prisme_home_1"
            )

            # Connexion to local database
            local_conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Q3fhllj2",
                database="prismathome"
            )

            # Cursor for the remote database
            remote_cursor = remote_conn.cursor()

            # Request for getting the remote user id
            remote_cursor.execute("SELECT id_user, login, password, connected FROM user")

            # Fetching all remote user data
            remote_users = remote_cursor.fetchall()

            # Cursor for the local database
            local_cursor = local_conn.cursor()

            for remote_user in remote_users:
                remote_id = remote_user[0]

                # Checking if the id exists locally
                local_cursor.execute("SELECT id_user FROM user WHERE id_user = %s", (remote_id,))

                if local_cursor.fetchone() is None:
                    # Copying the id if it doesn't exist locally
                    local_cursor.execute(
                        "INSERT INTO user (id_user, login, password, connected) VALUES (%s, %s, %s, %s)", remote_user)

            # Committing the changes in the local database
            local_conn.commit()

        except mysql.connector.Error as err:
            raise err
            print(f"Erreur MySQL : {err}")

        finally:
            # Closing the connections
            if remote_cursor:
                remote_cursor.close()
                remote_conn.close()
            if local_cursor:
                local_cursor.close()
                local_conn.close()

        messagebox.showinfo("Import user", "The import of user was successfully executed.")

    def import_sensor_type_from_remote_to_local(self):
        """!
        @brief This function connects to the remote and local database and fetch the sensor type from the remote
        database that doesn't appear in the local database and copy them locally
        @param self : the instance
        @return Nothing
        """
        try:
            # Connexion to remote database
            remote_conn = mysql.connector.connect(
                host="127.0.0.1",
                user="root",
                password="Q3fhllj2",
                database="prisme_home_1"
            )

            # Connexion to local database
            local_conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Q3fhllj2",
                database="prismathome"
            )

            # Cursor for the remote database
            remote_cursor = remote_conn.cursor()

            # Request for getting the remote type id
            remote_cursor.execute("SELECT id_type, type FROM sensor_type")

            # Fetching all remote sensor type data
            remote_sensor_types = remote_cursor.fetchall()

            # Cursor for the local database
            local_cursor = local_conn.cursor()

            for remote_sensor_type in remote_sensor_types:
                remote_id = remote_sensor_type[0]

                # Checking if the id exists locally
                local_cursor.execute("SELECT id_type FROM sensor_type WHERE id_type = %s", (remote_id,))

                if local_cursor.fetchone() is None:
                    # Copying the id if it doesn't exist locally
                    local_cursor.execute("INSERT INTO sensor_type (id_type, type) VALUES (%s, %s)", remote_sensor_type)

            # Committing the changes in the local database
            local_conn.commit()

        except mysql.connector.Error as err:
            print(f"Erreur MySQL : {err}")
        finally:
            # Closing the connections
            if remote_cursor:
                remote_cursor.close()
                remote_conn.close()
            if local_cursor:
                local_cursor.close()
                local_conn.close()

        messagebox.showinfo("Import sensor type", "The import of sensor type was successfully executed.")

    def import_config_from_remote_to_local(self):
        """!
        @brief This function connects to the remote and local database and fetch the configurations from the remote
        database that doesn't appear in the local database and copy them and the sensor_config associated to the config
        locally
        @param self : the instance
        @return Nothing
        """
        try:
            # Connexion to remote database
            remote_conn = mysql.connector.connect(
                host="127.0.0.1",
                user="root",
                password="Q3fhllj2",
                database="prisme_home_1"
            )

            # Connexion to local database
            local_conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Q3fhllj2",
                database="prismathome"
            )

            # Cursor for the remote database
            remote_cursor = remote_conn.cursor()

            # Request for getting the remote config id
            remote_cursor.execute("SELECT id_config, id_user, label, description FROM configuration")

            # Fetching all remote configuration data
            remote_configurations = remote_cursor.fetchall()

            # Cursor for the local database
            local_cursor = local_conn.cursor()

            for remote_configuration in remote_configurations:
                remote_id = remote_configuration[0]

                # Checking if the id_config already exists in the local configuration table
                local_cursor.execute("SELECT id_config FROM configuration WHERE id_config = %s", (remote_id,))
                config_exists = local_cursor.fetchone() is not None

                if not config_exists:
                    # Copying the config if it doesn't already exist
                    local_cursor.execute(
                        "INSERT INTO configuration (id_config, id_user, label, description) VALUES (%s, %s, %s, %s)",
                        remote_configuration)

                    # Now, check if there is corresponding data in the sensor_config table at remote
                    remote_cursor.execute(
                        "SELECT id_config, id_sensor_type, sensor_label, sensor_description FROM sensor_config WHERE id_config = %s",
                        (remote_id,))
                    remote_sensor_configs = remote_cursor.fetchall()

                    # Copying the sensor_config data to local database
                    for remote_sensor_config in remote_sensor_configs:
                        local_cursor.execute(
                            "INSERT INTO sensor_config (id_config, id_sensor_type, sensor_label, sensor_description) VALUES (%s, %s, %s, %s)",
                            remote_sensor_config)

            # Committing the changes in the local database
            local_conn.commit()

        except mysql.connector.Error as err:
            print(f"Erreur MySQL : {err}")
        finally:
            # Closing the connections
            if remote_cursor:
                remote_cursor.close()
                remote_conn.close()
            if local_cursor:
                local_cursor.close()
                local_conn.close()

        messagebox.showinfo("Import configuration", "The import of configuration was successfully executed.")
