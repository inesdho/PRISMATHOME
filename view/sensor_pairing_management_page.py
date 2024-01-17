import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import *

import mysql
import globals

from model import local
import model.local_mqtt
import time
import threading
import getpass


class SensorPairingManagement:
    def __init__(self, master):
        """!
       @brief The __init__ function sets the master frame in parameters as the frame that will contain all the widgets of
       this page and the variable that will be used
       @param self : the instance
       @param master : the master frame (created in the controller.py file)
       @return Nothing
       """

        # List of sensors already paired
        self.black_list = []

        # List to hold the label, description entries for each sensor, and sensor type ID
        self.sensor_entries = []

        # Set the master frame and creates the frame that will hold all the content of the page
        self.master = master
        self.frame = ttk.Frame(self.master)
        self.frame.pack(fill=tk.BOTH, expand=tk.TRUE)

        # Displays the title of the page
        label = ttk.Label(self.frame, text="SENSOR PAIRING", font=globals.global_font_title, foreground='#3daee9')
        label.pack(pady=30)

        # Creation of a canvas in order to add a scrollbar in case to many lines of sensors are displayed
        self.canvas = tk.Canvas(self.frame, bd=2, relief="ridge", highlightthickness=2)
        self.scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill="y")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Creation of the frame that will hold the values of the sensors
        self.frame_canvas = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), anchor='nw', window=self.frame_canvas)

    def show_page(self):
        """!
        @brief The show_page function creates and displays all the elements of the "Sensor pairing" page
        @param self : The instance
        @return Nothing
        """

        # Creation of the frame tate will contain the title of the field
        frame_title = ttk.Frame(self.frame_canvas)
        frame_title.pack(pady=5, fill=tk.BOTH, expand=tk.TRUE)

        # Create the title of the different field
        ttk.Label(frame_title, background="#3daee9", width=50, text="Sensor", borderwidth=0.5, relief="solid",
                  padding=5, anchor="center", font=globals.global_font_text).pack(side=tk.LEFT)
        ttk.Label(frame_title, background="#3daee9", width=20, text="Label", borderwidth=0.5, relief="solid",
                  padding=5,  anchor="center", font=globals.global_font_text).pack(side=tk.LEFT)
        ttk.Label(frame_title, background="#3daee9", width=80, text="Description", borderwidth=0.5, relief="solid",
                  padding=5,  anchor="center", font=globals.global_font_text).pack(side=tk.LEFT)

        self.sensor_entries = local.get_sensors_from_configuration(globals.global_id_config_selected)

        for index, sensor in enumerate(self.sensor_entries, start=1):
            self.create_labeled_entry(sensor, index)

        # Configure the scroll region to follow the content of the frame
        self.frame_canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def create_labeled_entry(self, sensor, index):
        """!
        @brief This function shows the label and the description of each sensor associated to the configuration chosen
        by the user
        @param self : the instance
        @param sensor : The sensor that need its information to be displayed
        @param index : The index of the sensor within its sensor type
        @return Nothing
        """
        data_frame = ttk.Frame(self.frame_canvas)
        data_frame.pack(pady=5, fill=tk.BOTH, expand=tk.TRUE)

        # Showing the type of the sensor
        ttk.Label(data_frame, text=sensor["type"] + " sensor " + str(index), width=50, anchor='w',
                  background="white", borderwidth=0.5, relief="solid", padding=5, font=globals.global_font_text).pack(side=tk.LEFT)

        # Creating a text widget tht will contain the label associated with the sensor
        ttk.Label(data_frame, text=sensor["label"], borderwidth=0.5, background="white", width=20,
                  relief="solid", padding=5, font=globals.global_font_text).pack(side=tk.LEFT)

        # Showing the description of the sensor
        ttk.Label(data_frame, background="white", width=80, text=sensor["description"], borderwidth=0.5,
                  relief="solid", padding=5, font=globals.global_font_text).pack(side=tk.LEFT)

        button_pairing = ttk.Button(data_frame, text=" ")
        button_pairing.pack(side=tk.LEFT, padx=5)

        # Adding the control button for the management of the sensor connection
        self.button_init(button_pairing, sensor)

    def center_window(self, window):
        """!
        @brief Center the window in the middle of the screen. Used for the pairing popup of pairing_a_sensor function
        @param window : the window to center

        @return None
        """
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()

        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height - 200) // 2

        window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    # Initialise the button to offer the user the option to pair a physical sensor
    def button_init(self, button_pairing, sensor):
        """!
        @brief button_init : THis functions edit the button in order to change the text that it displays and the function
        associated to it.
        @param self : The instance

        @return : None
        """
        button_pairing.config(text="Pairing", command=lambda: self.pairing_a_sensor(button_pairing, sensor, None))

    # Function to change the background while entering the label
    def on_enter_sensor_label(self, event):
        """!
        @brief choose_sensor : Function to change the background while entering the label
        @param event : The event containing the widget label

        @return : None
        """
        event.widget.configure(bg="lightblue")

    def on_leave_sensor_label(self, event):
        """!
        @brief choose_sensor : Function to recover default background while leaving a label
        @param event : The event containing the widget label

        @return : None
        """
        event.widget.configure(bg="white")

    def choose_sensor(self, button_pairing, sensor_selected, sensor_elt, popup, edit_sensor):
        """!
        @brief choose_sensor : This function is used to associate the sensor_elt to the real sensor by renaming the
        sensor in zigbee2mqtt with the correct label
        @param button_pairing : The button which has been clicked to open the popup
        @param sensor_selected : The dictionary of the real sensor from zigbee2mqtt containing the sensor details
        (ieee_address, name, ...)
        @param sensor_elt : The dictionary containing the sensor details filled by the user (label, description, type)
        @param popup : The popup created by pairing_a_sensor function
        @param edit_sensor : The name of the sensor being edited

        @return : None
        """

        if (model.local_mqtt.rename_sensor(sensor_selected['name'],
                                           sensor_elt["type"] + "/" + sensor_elt['label']) != 1):
            showinfo("Problem", "A problem occured while renaming")
            popup.grab_release()
            popup.destroy()
            return

        sensor_selected['name'] = sensor_elt["type"] + "/" + sensor_elt['label']
        # If an edit_sensor is specified we need to remove it from the list because it won't be in use anymore
        if edit_sensor:
            self.black_list.remove(edit_sensor["ieee_address"])
            children = button_pairing.master.winfo_children()
            if children:
                children[-1].destroy()

        self.black_list.append(sensor_selected["ieee_address"])

        # Add the ieee_address to the sensor_elt to save it for the db insert
        sensor_elt["ieee_address"] = sensor_selected["ieee_address"]

        # Popup close
        popup.grab_release()
        popup.destroy()

        button_pairing.config(text="Edit",
                              command=lambda: self.edit_the_pairing(button_pairing, sensor_selected, sensor_elt))

        button_pairing.master.winfo_children()[0].configure(text=sensor_selected["label"])

        match sensor_elt["type"]:
            case "Button":
                label_sensor_value = ttk.Label(button_pairing.master, text="Action : Unknown")
                label_sensor_value.pack(side=tk.LEFT, padx=10)
            case "Door":
                label_sensor_value = ttk.Label(button_pairing.master, text="Contact : Unknown")
                label_sensor_value.pack(side=tk.LEFT, padx=10)
            case "Motion":
                label_sensor_value = ttk.Label(button_pairing.master, text="Occupancy : Unknown")
                label_sensor_value.pack(side=tk.LEFT, padx=10)
            case "Vibration":
                label_sensor_value = ttk.Label(button_pairing.master, text="Vibration : Unknown")
                label_sensor_value.pack(side=tk.LEFT, padx=10)

        my_thread = threading.Thread(target=model.local_mqtt.get_sensor_value,
                                     args=(sensor_selected["name"], label_sensor_value))
        my_thread.start()

    def allow_sensor_join_management(self, button_pairing, sensor_elt, popup, edit_sensor):
        """!
        @brief allow_sensor_join_management : This function is used to allow the sensor to join zigbee2mqtt. This
        function wait until the sensor joins before calling choose_sensor function. The user must close the window to
        cancel.
        @param button_pairing : The button which has been clicked to open the popup
        @param sensor_elt : The dictionary containing the sensor details filled by the user (label, description, type)
        @param popup : The popup created by pairing_a_sensor function
        @param edit_sensor : The name of the sensor being edited

        @return : None
        """
        flag = False

        # Clear the popup
        for widget in popup.winfo_children():
            widget.destroy()

        # Display the new title
        label_title = tk.Label(popup, text="Waiting for a new sensor to connect", font=("Arial", 14, "bold"), padx=20,
                               pady=10)
        label_title.pack(padx=5, pady=5)

        # Display the instruction message
        label_message = tk.Label(popup, text="Please perform the physical manipulation on the sensor you want to pair. "
                                             "Refer to the documentation.", font=("Arial", 12), padx=20,
                                 pady=10, wraplength=popup.winfo_width())
        label_message.pack(padx=5, pady=5)

        # Creation of a scrollable frame to display all the sensors
        my_canvas = tk.Canvas(popup)
        my_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        my_scrollbar = ttk.Scrollbar(popup, orient="vertical", command=my_canvas.yview)
        my_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        my_canvas.configure(yscrollcommand=my_scrollbar.set)
        my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))
        scrollable_frame = ttk.Frame(my_canvas)
        my_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=400)

        if (model.local_mqtt.change_permit_join(True) != 1):
            showinfo("Error", "A problem occurred while changing the permit_join state")
            popup.grab_release()
            popup.destroy()
            return

        def on_click_new_sensor(event):
            nonlocal flag
            global new_sensor
            flag = True
            self.choose_sensor(button_pairing, new_sensor, sensor_elt, popup, edit_sensor)

        def display_new_sensor():
            """!
            @brief display_new_sensor is used to display the new sensor on the popup. This function is called as a
            thread in order not to block the program

            @return : None
            """
            nonlocal flag
            global new_sensor

            while not flag:
                new_sensor = model.local_mqtt.get_new_sensors()

                # Create a box frame to the sensor_label
                sensor_frame = tk.Frame(scrollable_frame, cursor="hand2", bg="white", pady=0)
                sensor_frame.pack(fill=tk.X, padx=10, pady=(5, 0), expand=True)

                # Display the sensor label
                sensor_label = tk.Label(sensor_frame, text=new_sensor["label"], padx=10, pady=10, bg="white")
                sensor_label.pack(fill=tk.X)

                # Add event click on the labbel
                # If the label is clicked the function "choose_sensor" will be called
                sensor_label.bind("<Button-1>", on_click_new_sensor)

                # Add event enter and leave for style
                sensor_label.bind("<Enter>", self.on_enter_sensor_label)
                sensor_label.bind("<Leave>", self.on_leave_sensor_label)

        # Create a thread for display_new_sensor function
        # Because display_new_sensor block the program while waiting for a new sensor
        # it allows the program to display label_title and label_message before the end of the function
        thread_display = threading.Thread(target=display_new_sensor)
        thread_display.start()

    def pairing_a_sensor(self, button_pairing, sensor, edit_sensor):
        """!
        @brief pairing_a_sensor : This function is used to display a popup to select a sensor to pair
        @param button_pairing : The button which has been clicked to open the popup
        @param sensor : The dictionary containing the sensor details (label, description, type)
        @param edit_sensor : The name of the sensor being edited

        @return : None
        """
        print("pairing the sensor : ", sensor)
        # Dictionary of sensor label related to their description in zigbee2mqtt
        # You must add the sensor description in this dictionary for every new sensor reference you add
        sensor_type_dictionary = {
            "Button": ["Aqara T1 wireless mini switch"],
            "Door": ["Aqara T1 door & window contact sensor"],
            "Vibration": ["Vibration sensor", "Aqara vibration sensor"],
            "Motion": ["Aqara P1 human body movement and illuminance sensor"]
        }
        try:
            # Get the sensors paired to zigbee2mqtt
            sensor_list = model.local_mqtt.get_all_sensors_on_zigbee2mqtt("all")

            # Creation of the popup
            popup_pairing = tk.Toplevel()
            popup_pairing.title("Pairing")
            popup_pairing.geometry('400x300')
            popup_pairing.resizable(False, False)

            print("Affichage de la popup ")

            # Center the popup
            self.center_window(popup_pairing)

            # Freeze the master window
            #popup_pairing.grab_set()

            # Display a label
            label_message = tk.Label(popup_pairing, text="Please select a sensor", font=("Arial", 14, "bold"), padx=20,
                                     pady=10)
            label_message.pack(padx=5, pady=5)

            # Creation of a box with a button to allow permit join
            join_frame = tk.Frame(popup_pairing, padx=5, pady=5)
            join_frame.pack(fill='both', expand=True, padx=10, pady=5)
            label_join = tk.Label(join_frame, text="Permit other sensors to join", font=("Arial", 12, "bold"))
            label_join.pack(side='left', fill='both')
            plus_button = tk.Button(join_frame, text="+", font=("Arial", 15, "bold"), cursor="hand2", bg="white", padx=7,
                                    pady=0,
                                    command=lambda: self.allow_sensor_join_management(button_pairing, sensor,
                                                                                      popup_pairing, edit_sensor))
            plus_button.pack(side='right', padx=5)

            # Creation of a scrollable frame to display all the sensors
            my_canvas = tk.Canvas(popup_pairing)
            my_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
            my_scrollbar = ttk.Scrollbar(popup_pairing, orient="vertical", command=my_canvas.yview)
            my_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            my_canvas.configure(yscrollcommand=my_scrollbar.set)
            my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))
            scrollable_frame = ttk.Frame(my_canvas)
            my_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=400)

            print("Getting the sensors")
            print("sensor list ", sensor_list)
            # Fill the scrollable frame with the available sensors
            for i in range(len(sensor_list)):
                print("Getting sensor boucle")
                # Check if the sensor is not already chosen
                if (sensor_list[i]["ieee_address"] not in self.black_list and sensor_list[i]["label"]
                        in sensor_type_dictionary[sensor["type"]]):
                    # Create a box frame to the sensor_label
                    sensor_frame = tk.Frame(scrollable_frame, cursor="hand2", bg="white", pady=0)
                    sensor_frame.pack(fill=tk.X, padx=10, pady=(5, 0), expand=True)

                    # Display the sensor label
                    sensor_label = tk.Label(sensor_frame, text=sensor_list[i]["label"], padx=10, pady=10, bg="white")
                    sensor_label.pack(fill=tk.X)

                    # Add event click on the labbel
                    # If the label is clicked the function "choose_sensor" will be called
                    sensor_label.bind("<Button-1>", lambda event, name=sensor_list[i], button=button_pairing,
                                                           sensor_elt=sensor, popup=popup_pairing,
                                                           editing=edit_sensor: self.choose_sensor(
                        button, name, sensor_elt, popup, editing))

                    # Add event enter and leave for style
                    sensor_label.bind("<Enter>", self.on_enter_sensor_label)
                    sensor_label.bind("<Leave>", self.on_leave_sensor_label)
        except Exception as e:
            print(f"\033[91mError popup pairing: {e}\033[0m")
        print("Fin boucle")

    def edit_the_pairing(self, button_pairing, sensor_selected, sensor_elt):
        """!
        @brief edit_the_pairing : Call the pairing_a_sensor function with the param edit_sensor=sensor_selected to edit
        it.
        @param button_pairing : The button which has been clicked to open the popup
        @param sensor_selected : The name of the real sensor from zigbee2mqtt
        @param sensor_elt : The dictionary containing the sensor details filled by the user (label, description, type)

        @return : None
        """
        print("Sensor " + sensor_elt["label"] + " : editing the pairing")
        self.pairing_a_sensor(button_pairing, sensor_elt, sensor_selected)

        # self.button_init(button_pairing, sensor_elt)

    def clear_page(self):
        """!
        @brief this function clears the content of the page
        @param self : The instance
        @return : None
        """
        self.canvas.destroy()
        self.frame.destroy()

    def on_validate_button_click(self, only_local):
        # TODO vérifier que tous les capteurs ont été appairées
        for sensor in self.sensor_entries:
            sensor["ieee_address"] = "0x1234567891237894"  # Adresse IEEE fictive pour les tests

        # Get the linux user connected
        user = getpass.getuser()

        # Create the observation and the sensors in the database
        local.create_observation_with_sensors(user, globals.global_participant_selected,
                                              globals.global_id_config_selected,
                                              globals.global_id_session_selected,
                                              globals.global_session_label_selected,
                                              self.sensor_entries, only_local)

        # Set True to stop the thread displaying sensor values
        globals.thread_done = True
        # Wait for the end of thread displaying sensor values
        time.sleep(1)
