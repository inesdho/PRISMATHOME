import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import *
import model.local_mqtt
import time
import threading


class SensorPairingManagement:
    def __init__(self, master):
        """!
       @brief The __init__ function sets the master frame in parameters as the frame that will contain all the widgets of
       this page
       @param the instance, the master frame (created in the controller.py file)
       @return Nothing
       """
        self.master = master
        self.frame = ttk.Frame(self.master)
        self.sensor_entries = []  # List to hold the label, description entries for each sensor, and sensor type ID

        self.frame.pack(fill=tk.BOTH, expand=tk.TRUE)

        # Displays the title of the page
        self.label_page = ttk.Label(self.frame, text="Sensor pairing", font=16, padding=10)
        self.label_page.pack(pady=20)

        # Creation of a canvas in order to add a scrollbar in case to many lines of sensors are displayed
        self.canvas = tk.Canvas(self.frame, bd=2, relief="ridge", highlightthickness=2)
        self.scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill="y")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.frame_canvas = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), anchor='nw', window=self.frame_canvas)


    def show_page(self):
        """!
        @brief The show_page function creates and displays all the elements of the "Sensor pairing" page
        @param The instance
        @return Nothing
        """

        black_list = []

        # Create entries for sensors
        for index, sensor in enumerate(self.get_sensors(), start=1):
            self.create_labeled_entry(sensor, index, black_list)


        # Configure the scroll region to follow the content of the frame
        self.frame_canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def create_labeled_entry(self, sensor, index, black_list):
        """!
        @brief This function shows the label and the description of each sensor associated to the configuration chosen
        by the user
        @param the instance
        @param sensor : The sensor that need its information to be displayed
        @param index : The index of the sensor within its sensor type
        @param black_list : The list of sensors already chosen
        @return Nothing
        """
        data_frame = ttk.Frame(self.frame_canvas)
        data_frame.pack(pady=5, fill=tk.BOTH, expand=tk.TRUE)

        label = ttk.Label(data_frame, text=sensor["type"] + " " + str(index), width=20, anchor='w')
        label.pack(side=tk.LEFT)

        # Showing the label of the sensor
        label_label = ttk.Label(data_frame, text="Label :", width=10)
        label_label.pack(side=tk.LEFT)
        # Creating a text widget tht will contain the label associated with the sensor
        self.create_an_entry_widget(sensor["label"], data_frame, 20)

        # Showing the description of the sensor
        description_label = ttk.Label(data_frame, text="\tDescription :", width=20)
        description_label.pack(side=tk.LEFT)
        # Creating a text widget tht will contain the description associated with the sensor
        self.create_an_entry_widget(sensor["description"], data_frame, 80)

        button_pairing = ttk.Button(data_frame, text=" ")
        button_pairing.pack(side=tk.LEFT, padx=5)

        # Adding the controll button for the management of the sensor connexion
        self.button_init(button_pairing, sensor, black_list)

    # Create a text widget that will contain the text in the parameter of the function
    def create_an_entry_widget(self, text, frame, width):
        """!
        @brief Create a text widget that will contain the text in the parameter of the function
        @param text : the text that needs to be displayed
        @param frame : the frame that will contain the widget
        @param width : the width of the widget
        @return None
        """
        sensor_entry = ttk.Entry(frame, width=width)
        # Adding the content of the text widget
        sensor_entry.insert(-1, text)
        sensor_entry.configure(state='readonly')
        sensor_entry.pack(side=tk.LEFT)

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
    def button_init(self, button_pairing, sensor, black_list):
        button_pairing.config(text="Pairing", command=lambda: self.pairing_a_sensor(button_pairing, sensor, black_list, None))

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

    def choose_sensor(self, button_pairing, sensor_selected, sensor_elt, black_list, popup, edit_sensor):
        """!
        @brief choose_sensor : This function is used to associate the sensor_elt to the real sensor by renaming the
        sensor in zigbee2mqtt with the correct label
        @param button_pairing : The button which has been clicked to open the popup
        @param sensor_selected : The dictionary of the real sensor from zigbee2mqtt containing the sensor details
        (iee_address, name, ...)
        @param sensor_elt : The dictionary containing the sensor details filled by the user (label, description, type)
        @param black_list : The list of sensors already chosen
        @param popup : The popup created by pairing_a_sensor function
        @param edit_sensor : The name of the sensor being edited

        @return : None
        """
        # TODO : Call rename sensor

        # If an edit_sensor is specified we need to remove it from the list because it wont be in use anymore
        if edit_sensor:
            black_list.remove(edit_sensor["ieee_address"])
            children = button_pairing.master.winfo_children()
            if children:
                children[-1].destroy()

        black_list.append(sensor_selected["ieee_address"])
        # TODO : Ajouter l'adresse mac à sensor elt
        print("the sensor " + sensor_selected["label"] + "was paired")
        popup.grab_release()
        popup.destroy()
        button_pairing.config(text="Edit",
                              command=lambda: self.edit_the_pairing(button_pairing, sensor_selected, sensor_elt,
                                                                    black_list))

        label_sensor = ttk.Label(button_pairing.master, text="")
        label_sensor.pack(side=tk.BOTTOM)

        # Créer un thread en passant la fonction et les paramètres
        my_thread = threading.Thread(target=model.local_mqtt.get_sensor_value, args=(sensor_selected["name"], label_sensor))

        # Démarrer le thread
        my_thread.start()

        showinfo("Capteur sélectionné", f"Vous avez sélectionné le capteur {sensor_selected}")

    def allow_sensor_join_management(self, button_pairing, sensor_elt, black_list, popup, edit_sensor):
        """!
        @brief allow_sensor_join_management : This function is used to allow the sensor to join zigbee2mqtt. This
        function wait until the sensor joins before calling choose_sensor function. The user must close the window to
        cancel.
        @param button_pairing : The button which has been clicked to open the popup
        @param sensor_elt : The dictionary containing the sensor details filled by the user (label, description, type)
        @param black_list : The list of sensors already chosen
        @param popup : The popup created by pairing_a_sensor function
        @param edit_sensor : The name of the sensor being edited

        @return : None
        """
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

        #model.local_mqtt.change_permit_join(True)
        def display_new_sensor():
            """!
            @brief display_new_sensor is used to display the new sensor on the popup. This function is called as a
            thread in order not to block the program

            @return : None
            """

            # TODO : Faire un while True
            #new_sensor=model.local_mqtt.get_new_sensor()
            # New sensor test
            new_sensor = {
                'name': "Test",
                'ieee_address': "123456789",
                'label': "Je suis un capteur aqara"
            }

            # Create a box frame to the sensor_label
            sensor_frame = tk.Frame(scrollable_frame, cursor="hand2", bg="white", pady=0)
            sensor_frame.pack(fill=tk.X, padx=10, pady=(5, 0), expand=True)

            # Display the sensor label
            sensor_label = tk.Label(sensor_frame, text=new_sensor["label"], padx=10, pady=10, bg="white")
            sensor_label.pack(fill=tk.X)

            # Add event click on the labbel
            # If the label is clicked the function "choose_sensor" will be called
            sensor_label.bind("<Button-1>", lambda event, name=new_sensor, button=button_pairing, list=black_list,
                                                   sensor=sensor_elt, popup_join=popup,
                                                   editing=edit_sensor: self.choose_sensor(
                button, name, sensor, list, popup_join, editing))

            # Add event enter and leave for style
            sensor_label.bind("<Enter>", self.on_enter_sensor_label)
            sensor_label.bind("<Leave>", self.on_leave_sensor_label)

        # Create a thread for display_new_sensor function
        # Because display_new_sensor block the program while waiting for a new sensor
        # it allows the program to display label_title and label_message before the end of the function
        thread_display = threading.Thread(target=display_new_sensor)
        thread_display.start()

        # If we get the sensor : then call the function choose_sensor(self, button_pairing, sensor_selected, sensor_elt, black_list, popup)
        # Else showerror("Error", "The sensor could not connect to the system")

    def pairing_a_sensor(self, button_pairing, sensor, black_list, edit_sensor):
        """!
        @brief pairing_a_sensor : This function is used to display a popup to select a sensor to pair
        @param button_pairing : The button which has been clicked to open the popup
        @param sensor : The dictionary containing the sensor details (label, description, type)
        @param black_list : The list of sensors already chosen
        @param edit_sensor : The name of the sensor being edited

        @return : None
        """
        # Get the sensors paired to zigbee2mqtt
        sensor_list = model.local_mqtt.get_all_sensors_on_zigbee2mqtt("all")

        # Creation of the popup
        popup_pairing = tk.Toplevel()
        popup_pairing.title("Pairing")
        popup_pairing.geometry('400x300')
        popup_pairing.resizable(False, False)

        # Center the popup
        self.center_window(popup_pairing)

        # Freeze the master window
        popup_pairing.grab_set()

        # Display a labbel
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
                                command=lambda: self.allow_sensor_join_management(button_pairing, sensor, black_list,
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

        # Fill the scrollable frame with the available sensors
        for i in range(len(sensor_list)):
            # Check if the sensor is not already chosen
            if sensor_list[i]["ieee_address"] not in black_list:
                # Create a box frame to the sensor_label
                sensor_frame = tk.Frame(scrollable_frame, cursor="hand2", bg="white", pady=0)
                sensor_frame.pack(fill=tk.X, padx=10, pady=(5, 0), expand=True)

                # Display the sensor label
                sensor_label = tk.Label(sensor_frame, text=sensor_list[i]["label"], padx=10, pady=10, bg="white")
                sensor_label.pack(fill=tk.X)

                # Add event click on the labbel
                # If the label is clicked the function "choose_sensor" will be called
                sensor_label.bind("<Button-1>", lambda event, name=sensor_list[i], button=button_pairing, list=black_list,
                                                       sensor_elt=sensor, popup=popup_pairing,
                                                       editing=edit_sensor: self.choose_sensor(
                    button, name, sensor_elt, list, popup, editing))

                # Add event enter and leave for style
                sensor_label.bind("<Enter>", self.on_enter_sensor_label)
                sensor_label.bind("<Leave>", self.on_leave_sensor_label)

    # TODO INDUS same ici, mais pour modifier l'appairage du capteur et donc le désappairé, pas besoin de retourner quoi que ce soit (enfin je crois)
    def edit_the_pairing(self, button_pairing, sensor_selected, sensor_elt, black_list):
        """!
        @brief edit_the_pairing : Call the pairing_a_sensor function with the param edit_sensor=sensor_selected to edit
        it.
        @param button_pairing : The button which has been clicked to open the popup
        @param sensor_selected : The name of the real sensor from zigbee2mqtt
        @param sensor_elt : The dictionary containing the sensor details filled by the user (label, description, type)
        @param black_list : The list of sensors already chosen

        @return : None
        """
        print("Sensor " + sensor_elt["label"] + " : editing the pairing")
        self.pairing_a_sensor(button_pairing, sensor_elt, black_list, sensor_selected)

        # self.button_init(button_pairing, sensor_elt)

    # TODO INES A voir comment tu le sens INES mais certianes des fonctions ci-dessous sont les mêmes que dans summary_window, est ce que ça vaudrait le coup de faire un fichier
    # TODO spécial qui fait que retourner des résultats de requêtes comme ça ?

    def get_sensors(self):
        # TODO INES la fonction doit retourner la liste des capteurs associés à la configuration en cours
        """
        query = (
            "SELECT sc.label AS sensor_label, sc.description AS sensor_description, st.type AS sensor_type "
            "FROM Sensor_config sc "
            "JOIN Sensor_type st ON sc.id_sensor_type = st.id_type "
            "WHERE sc.id_config = %s "
            "ORDER BY st.type"  # Tri par le type de capteurs
        )

        cursor.execute(query, (id_config,))
        results = cursor.fetchall()
        """
        # Fake result for test
        results = [
            ("Capteur1", "Description du capteur 1", "button"),
            ("Capteur2", "Description du capteur 2", "button"),
            ("Capteur3", "Description du capteur 3", "door"),
            ("Capteur4", "Description du capteur 4", "vibration"),
            ("Capteur5", "Description du capteur 5", "motion")
        ]
        # The list of sensors' dictionary
        sensors = []

        # Fill the sensor list from result
        for row in results:
            sensor_label = row[0]
            sensor_description = row[1]
            sensor_type = row[2]

            sensors.append({
                "label": sensor_label,
                "description": sensor_description,
                "type": sensor_type
            })

        return sensors

    def clear_page(self):
        """!
        @brief this function clears the content of the page
        @param self : The instance
        @return : None
        """
        self.canvas.destroy()
        self.frame.destroy()


