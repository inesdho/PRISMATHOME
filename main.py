from controller.controller import App
from controller.update_local_database import UpdateLocalDatabase
import time
import tkinter as tk
from tkinter import messagebox
from model import remote
from model import local

if __name__ == "__main__":
    # Starting the application
    app = App()
    local.connect_to_local_db()
    remote.connect_to_remote_db()

    if messagebox.askyesno("Import data", "Do you want to try to import data from the remote database into the local."
                                          "database ?"):
        try:
            # Try to update the local database with the data from the remote database
            UpdateLocalDatabase()
        except Exception as e:
            # Displaying an error message
            tk.Tk().withdraw()
            messagebox.showerror("Erreur", f"An error occurred while trying to update the local database : {str(e)}")
            app.destroy()

    app.mainloop()





