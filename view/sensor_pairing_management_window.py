import threading
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import *

class SensorPairingManagement:
    def __init__(self, master):
        self.master = master
        self.frame = ttk.Frame(self.master)

    def show_page(self):
        # Create a main frame which will be centered in the window
        self.frame = tk.Frame(self.master)
        self.frame.pack(expand=True)

        # Create entries for sensors
        for sensor in self.get_sensors():
            self.create_labeled_entry(sensor)

    # Helper function to create a labeled entry with two text boxes, one for label and one for description
    def create_labeled_entry(self, sensor_id):
        data_frame = ttk.Frame(self.frame)
        data_frame.pack(pady=5, fill=tk.BOTH, expand=tk.TRUE)

        label = ttk.Label(data_frame, text=sensor_id, width=20, anchor='w')
        label.pack(side=tk.LEFT)

        # Showing the label of the sensor
        label_label = ttk.Label(data_frame, text="Label :", width=10)
        label_label.pack(side=tk.LEFT)
        # Creating a text widget tht will contain the label associated with the sensor
        self.create_a_text_widget(self.get_sensor_label(sensor_id), data_frame, 20)

        # Showing the description of the sensor
        description_label = ttk.Label(data_frame, text="\tDescription :", width=20)
        description_label.pack(side=tk.LEFT)
        # Creating a text widget tht will contain the description associated with the sensor
        self.create_a_text_widget(self.get_sensor_description(sensor_id), data_frame, 50)

        button_pairing = ttk.Button(data_frame, text=" ")
        button_pairing.pack(side=tk.LEFT)

        # Adding the controll button for the management of the sensor connexion
        self.button_init(button_pairing, sensor_id)


    # Create a text widget that will contain the text in the parameter of the function
    def create_a_text_widget(self, text, frame, width):
        label_text = tk.Text(frame, height=1, width=width)
        # Adding the content of the text widget
        label_text.insert(1.0, text)
        label_text.configure(state='disabled', font=("Calibri", 11))
        label_text.pack(side=tk.LEFT, expand=tk.FALSE)


    # Initialise the button to offer the user the option to pair a physical snesor
    def button_init(self, button_pairing, sensor_id):
        button_pairing.config(text="Pairing", command=lambda: self.pairing_a_sensor(button_pairing, sensor_id))

    # Try to pair a sensor
    def pairing_a_sensor(self, button_pairing, sensor_id):

        if self.is_paired(button_pairing, sensor_id):
            #If the pairing was a success, show the message change the label of the button and the fonciton it's ralated to
            print("the sensor "+ sensor_id + " was paired")
            button_pairing.config(text="Edit", command=lambda: self.edit_the_pairing(button_pairing, sensor_id))
        else:
            showerror("Error", "The sensor could not connect to the system")





    # TODO INDUS est ce que vous pourriez me remplacer ça par une fonction qui me return true si l'appareillage c'est bien passé sinon false, je vous ai mis l'ID du sensor
    # TODO en cours d'appareillage en paramètre de fonction si jaja. J'ai aussi passé en param le bouton histoire de changer sa fonction et son affichage pour la partie cancel de l'appairage
    def is_paired(self, button_pairing, sensor_id):
        button_pairing.config(text="Cancel",  command=lambda: self.cancel_the_pairing(button_pairing, sensor_id))
        # Si vous avez qqch à faire c'est ici qu'il faut le mettre et modifier le return
        return True

    #TODO INDUS same ici, mais pour interrompre le pairing lorsque l'utilisateur a cliqué sur le bouton cancel, pas besoin de retourner quoi que ce soit
    def cancel_the_pairing(self, button_pairing, sensor_id):
        #Si vous avez qqch à faire c'est ici
        print("Sensor " + sensor_id + " : cancelling the pairing")
        self.button_init(button_pairing,sensor_id)


    # TODO INDUS same ici, mais pour modifier l'appairage du capteur et donc le désappairé, pas besoin de retourner quoi que ce soit (enfin je crois)
    def edit_the_pairing(self, button_pairing, sensor_id):
        # Si vous avez qqch à faire c'est ici
        print("Sensor " + sensor_id + " : editing the pairing")
        self.button_init(button_pairing, sensor_id)





    # TODO INES A voir comment tu le sens INES mais certianes des fonctions ci-dessous sont les mêmes que dans summary_window, est ce que ça vaudrait le coup de faire un fichier
# TODO spécial qui fait que retourner des résultats de requêtes comme ça ?

    def get_sensors(self):
        # TODO INES le fonction doit retourner la liste des capteurs associés à la configuration en cours
        return ['id_sensor_1', 'id_sensor_2', 'id_sensor_3', 'id_sensor_4']

    def get_sensor_label(self, id_sensor):
        # TODO INES Modifier la fonction pour qu'elle retourne le label d'un capteur en fonction de son id
        return "Label du capteur " + id_sensor

    def get_sensor_description(self, id_sensor):
        # TODO INES Modifier la fonction pour qu'elle retourne la description d'un capteur en fonction de son id
        return "Description du capteur" + id_sensor


    def clear_page(self):
        self.frame.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = SensorPairingManagement(root)
    app.show_page()
    root.mainloop()

