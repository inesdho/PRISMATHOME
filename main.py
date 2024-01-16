from controller.controller import App
from controller.update_local_database import UpdateLocalDatabase
from tkinter import messagebox
import threading
from model import remote
from model import local

if __name__ == "__main__":

    # Connect to local db
    local.connect_to_local_db()

    # Connect to remote db. With a thread in order not to block the program
    connection_thread = threading.Thread(target=remote.connect_to_remote_db)
    connection_thread.start()

    print("START")

    # Checking the user's response after the main loop
    if messagebox.askyesno("Import data", "Do you want to try to import data from the remote database into "
                                             "the local database?"):
        try:
            # Try to update the local database with the data from the remote database
            UpdateLocalDatabase()
        except Exception as e:
            messagebox.showerror("Erreur", f"An error occurred while trying to update the local database: {str(e)}")
            print('passé par le except')

    # Creating an instance of the application
    app = App()

    # Starting the main event loop
    app.mainloop()

