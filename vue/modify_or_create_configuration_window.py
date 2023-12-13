import tkinter as tk
from tkinter import ttk

import mysql.connector
from vue.login_as_admin_window import LoginAsAdministrator


class ModifyOrCreateConfiguration:
    def __init__(self, master):
        self.master = master
        self.frame = ttk.Frame(self.master)

    def show_page(self, login_value):
        self.frame = ttk.Frame(self.master)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Logout Button
        logout_button = tk.Button(self.master, text="Log out")
        logout_button.place(relx=0.9, rely=0.01)  # Position the logout button above the frames

        # Left Frame for Scenario Selection
        left_frame = tk.Frame(self.master, bd=2, relief="sunken", padx=5, pady=5)
        left_frame.place(relx=0.02, rely=0.09, relwidth=0.46, relheight=0.50)

        tk.Label(left_frame, text="Scenario name :").pack(anchor="nw")
        self.scenario_combobox = ttk.Combobox(left_frame, values=["Example", "Exemple 2", "Exemple 3"],
                                              state="readonly",
                                              width=30)
        self.scenario_combobox.set("Example")
        self.scenario_combobox.pack(fill="x")

        modify_button = tk.Button(left_frame, text="Modify the configuration")
        modify_button.pack(side="bottom", fill="x")

        # Right Frame for Scenario Creation
        right_frame = tk.Frame(self.master, bd=2, relief="sunken", padx=5, pady=5)
        right_frame.place(relx=0.50, rely=0.09, relwidth=0.48, relheight=0.50)

        tk.Label(right_frame, text="Scenario name :").pack(anchor="nw")
        self.name_entry = tk.Entry(right_frame)
        self.name_entry.pack(fill="x")

        tk.Label(right_frame, text="Description :").pack(anchor="nw")
        # Create a Text widget for multi-line text entry
        self.description_text_entry = tk.Text(right_frame, height=5)  # Height is set to 5 lines
        self.description_text_entry.pack(fill="x")

        create_button = tk.Button(right_frame, text="Create a configuration",
                                  command=lambda: self.on_create_configuration_button_click(login_value))
        create_button.pack(side="bottom", fill="x")

    def on_create_configuration_button_click(self, login_value):
        scenarioname = self.name_entry.get()
        description = self.description_text_entry.get("1.0", "end-1c")

        admin_login = LoginAsAdministrator(self.master)
        # TODO réccuèpre l'id de l'admin en fonction de la valeur du login que je t'ai mis en paramètre
        # id_user = admin_login.get_id_user_by_admin()
        id_user = 1

        num_config = self.get_number_config_create_by_admin(id_user) + 1

        id_config = str(id_user) + "-" + str(num_config)

        # Connexion à la base de données MySQL
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="prismathome"
        )
        cursor = conn.cursor()

        # Exécutez une requête
        query = "INSERT INTO configuration (id_config, id_user, label, description)VALUES(%s, '1', %s, %s)"
        cursor.execute(query, (id_config, scenarioname, description))
        conn.commit()

        # Fermez la connexion à la base de données
        cursor.close()
        conn.close()

    def get_number_config_create_by_admin(self, id_user):
        # Connexion à la base de données MySQL
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="prismathome"
        )
        cursor = conn.cursor()

        # Exécutez une requête
        query = "SELECT COUNT(*) FROM configuration WHERE id_user = %s"
        cursor.execute(query, (id_user,))

        # Récupérer le résultat
        count = cursor.fetchone()[0]

        # Fermez la connexion à la base de données
        cursor.close()
        conn.close()

        return count
