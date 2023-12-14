import tkinter as tk
from tkinter import ttk, messagebox

import mysql.connector
import globals

class LoginAsAdministrator:
    def __init__(self, master):
        self.master = master
        self.frame = ttk.Frame(self.master)

    def show_page(self):
        self.frame = ttk.Frame(self.master)
        self.frame.pack(fill=tk.BOTH, expand=True)

        label = ttk.Label(self.frame, text="Connexion Administrator", font=16)
        label.pack(pady=20)

        # login input
        login_label = ttk.Label(self.frame, text="Login")
        login_label.pack()
        self.login_entry = ttk.Entry(self.frame)
        self.login_entry.pack(pady=10)

        # password input
        password_label = ttk.Label(self.frame, text="Password")
        password_label.pack()
        self.password_entry = ttk.Entry(self.frame, show="*")  # Hide password input
        self.password_entry.pack(pady=10)

        # Afficher le cadre de la page de connexion en tant qu'administrateur
        self.frame.pack(fill=tk.BOTH, expand=True)

    def clear_page(self):
        # Destroy the frame
        self.frame.destroy()

    # Get the data from the user input
    def connexion_admin(self):
        username = self.login_entry.get()
        password = self.password_entry.get()

        print("connexion as admin")

        # Valisation automatique pour fonctionnement sans conncexion, commenter la ligne pour un fonctionnement avec BDD et supprimer la ligen avant la fin du projet
        #return True

        # Connexion à la base de données MySQL
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="prismathome"
        )
        cursor = conn.cursor()

        # Exécutez une requête
        query = "SELECT * FROM user WHERE login=%s AND password=%s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()

        # Vérifiez si l'utilisateur a été trouvé dans la base de données
        if user:
            globals.id_user = user[0]
            query_update = "UPDATE prismathome.user SET connected=1 WHERE login=%s AND password=%s"
            cursor.execute(query_update, (username, password))
            conn.commit()
            messagebox.showinfo("Connexion réussie", "Bienvenue, {}".format(username))

        else:
            messagebox.showerror("Erreur de connexion", "Nom d'utilisateur ou mot de passe incorrect")

        # Fermez la connexion à la base de données
        cursor.close()
        conn.close()

