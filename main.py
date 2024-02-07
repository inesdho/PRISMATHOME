from controller.controller import App
from utils.update_local_database import UpdateLocalDatabase
from tkinter import messagebox
import threading
from model import remote
from model import local
from utils import globals

if __name__ == "__main__":

    # Connect to local db
    if local.connect_to_local_db() == 0:
        messagebox.showerror("Error", f"Impossible to connect to local data base (Connection time out)")

    # Set the observation mode by getting it
    globals.global_observation_mode = local.get_observation_mode()

    # Connect to remote db. With a thread in order not to block the program
    connection_thread = threading.Thread(target=remote.connect_to_remote_db)
    connection_thread.start()

    # Creating an instance of the application
    app = App()

    # Checking the user's response after the main loop
    if messagebox.askyesno("Import data", "Do you want to try to import data from the remote database into "
                                             "the local database?"):
        try:
            # Try to update the local database with the data from the remote database
            UpdateLocalDatabase()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while trying to update the local database: {str(e)}")


    # Starting the main event loop
    app.mainloop()




