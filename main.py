from controller.controller import App
from controller.update_local_database import UpdateLocalDatabase
from tkinter import messagebox

if __name__ == "__main__":
    # Creating an instance of the application
    app = App()

    # Checking the user's response after the main loop
    if messagebox.askyesno("Import data", "Do you want to try to import data from the remote database into "
                                             "the local database?"):
        try:
            # Try to update the local database with the data from the remote database
            UpdateLocalDatabase()
        except Exception as e:
            messagebox.showerror("Erreur", f"An error occurred while trying to update the local database: {str(e)}")
            print('passé par le except')

    # Starting the main event loop
    app.mainloop()








