import tkinter as tk
from tkinter import ttk

import mysql.connector
from ttkthemes.themed_style import ThemedStyle
import globals

from view.login_as_admin_page import LoginAsAdministrator


class ModifyOrCreateConfiguration:
    def __init__(self, master):
        self.master = master
        self.frame = ttk.Frame(self.master)

    def show_page(self):
        self.frame = ttk.Frame(self.master)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Left Frame for Scenario Selection
        self.left_frame = tk.Frame(self.master, bd=2, relief="sunken", padx=5, pady=5)
        self.left_frame.place(relx=0.02, rely=0.09, relwidth=0.46, relheight=0.50)

        label_scenario_name = tk.Label(self.left_frame, text="Scenario name :")
        label_scenario_name.pack(anchor="nw")
        self.scenario_combobox = ttk.Combobox(self.left_frame, values=["Example", "Exemple 2", "Exemple 3"],
                                              state="readonly",
                                              width=30)
        self.scenario_combobox.set("Example")
        self.scenario_combobox.pack(fill="x")

        # Right Frame for Scenario Creation
        self.right_frame = tk.Frame(self.master, bd=2, relief="sunken", padx=5, pady=5)
        self.right_frame.place(relx=0.50, rely=0.09, relwidth=0.48, relheight=0.50)

        tk.Label(self.right_frame, text="Scenario name :").pack(anchor="nw")
        self.name_entry = tk.Entry(self.right_frame)
        self.name_entry.pack(fill="x")

        tk.Label(self.right_frame, text="Description :").pack(anchor="nw")
        # Create a Text widget for multi-line text entry
        self.description_text_entry = tk.Text(self.right_frame, height=5)  # Height is set to 5 lines
        self.description_text_entry.pack(fill="x")


    def on_create_configuration_button_click(self):
        scenarioname = self.name_entry.get()
        description = self.description_text_entry.get("1.0", "end-1c")


        # RETURN TRUE POUR TESTER LES REDIRECTIONS SANS LA BDD
        #return True

        admin_login = LoginAsAdministrator(self.master)
        # TODO voir apres que la redirection est faite pour recuperer l'id_user de la page de connexion
        id_user = globals.global_id_user
        print(id_user)
        num_config = self.get_number_config_create_by_admin(id_user) + 1

        id_config = str(id_user) + "-" + str(num_config)
        globals.global_id_config=id_config
        print("valeur de l'id user")
        print(id_user)
        # Connexion à la base de données MySQL
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="prismathome"
        )
        cursor = conn.cursor()

        # Exécutez une requête
        query = "INSERT INTO configuration (id_config, id_user, label, description)VALUES(%s, %s, %s, %s)"
        cursor.execute(query, (id_config, id_user, scenarioname, description))
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

    def clear_page(self):
        # Destroy the frame
        self.frame.destroy()
        self.right_frame.destroy()
        self.left_frame.destroy()