"""!
@mainpage Prisme@home project documentation

@section description_main Description
This project has been realized in the frame of a end of study project.

@section notes_main Notes
Project realized by 5 students from IG2I.

@file reception.py

@brief This is the main project file for collecting the informations with the sensors.
        In this file we create the mqtt client and subscribe to the sensors we need.

@author Naviis-Brain

@version 1.0

@date 28th Decembre 2023
"""
import paho.mqtt.client as mqtt
import sys
from controller import treatment
import os
import getpass
import signal
import time
import model.local_mqtt

## Constant for the broker port
BROKER_PORT = 1883
## Constant for the broker addr
BROKER_ADDR = "127.0.0.1"

def on_message(client, userdata, msg):
    treatment.data_treatment(client, userdata, msg)

if __name__ == "__main__":
    # Connection to local db
    treatment.local.connect_to_local_db()

    ## The mqtt client to collect the data from the broker
    coordinator = mqtt.Client("Coordinator")

    ## The on_message function of the mqtt client
    coordinator.on_message = on_message

    # Connection to mqtt broker
    model.local_mqtt.connect_to_mqtt_broker(coordinator)

    # Subscribe to every sensor paired
    for i in range(len(sys.argv)-1):
        print("subscribe : zigbee2mqtt/"+sys.argv[i+1])
        coordinator.subscribe("zigbee2mqtt/"+sys.argv[i+1])

    """TODO : Déplacer cette partie dans le main program"""
    pid_parent = os.getppid()
    pid = os.getpid()
    print("Le PID de ce processus est :", pid)
    print("Le user qui execute le prgm est ", getpass.getuser())
    print("Envoi d'un signal au père")
    os.kill(pid_parent, signal.SIGTERM)
    """ ******  Fin todo ************** """

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # TODO : Faire une loop jusqu'à réception d'un signal SIGTERM
    coordinator.loop_forever()

    db.close()
