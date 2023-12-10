import tkinter as tk
from tkinter import ttk

import mysql.connector


class MyApplication:
    def __init__(self, root):
        self.root = root
        self.create_gui()

    def create_gui(self):
        # Create the main window

        self.root.title("PRISM@Home")

        # Set the window size
        self.root.geometry("800x400")

        # Logout Button
        logout_button = tk.Button(root, text="Log out")
        logout_button.place(relx=0.9, rely=0.01)  # Position the logout button above the frames

        # Left Frame for Scenario Selection
        left_frame = tk.Frame(root, bd=2, relief="sunken", padx=5, pady=5)
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
        right_frame = tk.Frame(root, bd=2, relief="sunken", padx=5, pady=5)
        right_frame.place(relx=0.50, rely=0.09, relwidth=0.48, relheight=0.50)

        tk.Label(right_frame, text="Scenario name :").pack(anchor="nw")
        self.name_entry = tk.Entry(right_frame)
        self.name_entry.pack(fill="x")

        tk.Label(right_frame, text="Description :").pack(anchor="nw")
        # Create a Text widget for multi-line text entry
        self.description_text_entry = tk.Text(right_frame, height=5)  # Height is set to 5 lines
        self.description_text_entry.pack(fill="x")

        create_button = tk.Button(right_frame, text="Create a configuration",
                                  command=self.on_create_configuration_button_click)
        create_button.pack(side="bottom", fill="x")

        # Start the GUI event loop
        root.mainloop()

    def on_create_configuration_button_click(self):
        scenarioname = self.name_entry.get()
        description = self.description_text_entry.get("1.0", "end-1c")

        num_config = self.create_id_config('1') + 1
        id_config = id_user + "-" + num_config

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
        cursor.execute(query, (num_config, scenarioname, description))
        conn.commit()

        # Fermez la connexion à la base de données
        cursor.close()
        conn.close()

    def create_id_config(self, id_user):
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


if __name__ == "__main__":
    root = tk.Tk()
    app = MyApplication(root)
    root.mainloop()
