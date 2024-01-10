from controller.controller import App
from controller.update_local_database import UpdateLocalDatabase
import time
import tkinter as tk
from tkinter import messagebox

if __name__ == "__main__":
    try:
        # Try to update the local database with the data from the remote database
        UpdateLocalDatabase()
    except Exception as e:
        # Displaying an error message
        tk.Tk().withdraw()
        messagebox.showerror("Erreur", f"An error occurred while trying to update the local database : {str(e)}")

    # Lancement de l'application
    app = App()
    app.mainloop()



