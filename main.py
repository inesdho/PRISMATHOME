"""!
@mainpage Prisme@home project documentation

@section description_main Description
This project has been realized in the frame of an end of study project.

The Prisme at Home project aims to observe the behavior of participants in the study within their homes. In modern
research methodologies, it's crucial to gather data in naturalistic settings to ensure its validity and
applicability. By deploying sensors and data collection mechanisms in participants' homes, this project facilitates
the gathering of rich, real-world data without the biases introduced by laboratory settings.

The realization of this project is necessary as it will enable the reliable, timely, and maximized collection of
data. Currently, these data are gathered by surveying participants with targeted questions or by conducting studies
within the institute. However, such approaches are limited in scope and may not fully capture the nuances of
participants' behaviors in their daily lives.

In this document, we have developed the designs of the functions required for the PRISME AT HOME project. These
designs cover both the functions necessary for the system and those required for administration, ensuring seamless
data collection, management, and analysis.

This project was realized by 5 students from IG2I - Centrale Lille.
Paul Monier - Matteo Cucco - Charly Trevette - Ines D'houdetot - Mathilde Dumont.

@file main.py

@brief This is the main project file.

@author Naviis-Brain

@version 1.0

@date 31st January 2024
"""
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




