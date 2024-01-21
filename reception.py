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
from model import local
from model import remote
from model import local_mqtt
import os
import getpass
import signal
import time
import subprocess
from datetime import datetime
import threading
from system import system_function

## Constant for the broker port
BROKER_PORT = 1883
## Constant for the broker addr
BROKER_ADDR = "127.0.0.1"

pid_parent = None

pid_start_and_stop = None

coordinator = None

def get_pid_of_script(script_name):
    """!
    @brief Get the pid of the script "script_name"
    @param script_name The name of the script that we want to get the pid
    @return The pid of the script "script_name"
    """
    try:
        # Exécution de la commande 'ps' pour obtenir les processus en cours
        process = subprocess.run(['ps', 'aux'], stdout=subprocess.PIPE, text=True)
        # Filtrage des lignes qui contiennent le nom du script
        lines = process.stdout.split('\n')
        for line in lines:
            if script_name in line:
                parts = line.split()
                # Le PID est généralement le deuxième élément dans la sortie de 'ps aux'
                return int(parts[1])
    except Exception as e:
        print(f"Erreur lors de la recherche du PID: {e}")
    return None

def handler_program_stop(signum, frame):
    """!
    Wait for the signal SIGTERM coming from start_and_stop.py
    when there is a shut-down request. Then close the program.

    @param signum : The signal number.
    @param frame : The current stack frame.

    @return None
    """
    global pid_parent, pid_start_and_stop, coordinator

    local_mqtt.check_availability_stop = True

    # Stop the program
    coordinator.loop_stop()
    coordinator.disconnect()

    print("signum : " + str(signum))
    print("SIGUSR2 " + str(signal.SIGUSR2))
    pid_start_and_stop = get_pid_of_script("start_and_stop.py")
    print("pid_start_and_stop :", pid_start_and_stop)

    # Register the datetime when the signal was received
    datetime_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    print("POUR ETRE SUR")
    # If the signal come from start_and_stop program (SIGUSR2) :
    if signum == signal.SIGUSR2:
        print("signum = signal.SIGNUM")
        # Send a monitoring message that the system is shut down
        local.monitor_system_start_stop(datetime_now, 0)
        # Send a signal to start_and_stop program to indicate that the program is closed
        print("BEFORE SIGNAL SENT")
        system_function.send_signal(pid_start_and_stop, "SIGTERM")
        print("Signal sent")
    else:
        print("signum != signal.SIGNUM")
        print("SIGNAL NOT SENT")
        # Send a monitoring message that the observation is stopped
        local.monitor_observation_start_stop(datetime_now, 0)


def on_message(client, userdata, msg):
    print("message received 11")
    treatment.data_treatment(client, userdata, msg)


if __name__ == "__main__":

    # Connection to local db
    local.connect_to_local_db()

    # Connect to remote db. With a thread in order not to block the program
    connection_thread = threading.Thread(target=remote.connect_to_remote_db)
    connection_thread.start()

    ## The mqtt client to collect the data from the broker
    coordinator = mqtt.Client("Coordinator")

    ## The on_message function of the mqtt client
    coordinator.on_message = on_message

    # Connection to mqtt broker
    local_mqtt.connect_to_mqtt_broker(coordinator)

    # Subscribe to every sensor paired
    for i in range(len(sys.argv) - 1):
        print("subscribe : zigbee2mqtt/" + sys.argv[i + 1])
        coordinator.subscribe("zigbee2mqtt/" + sys.argv[i + 1])

    datetime_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    # Get the parent process pid
    pid_parent = os.getppid()

    print(f"pid_parent :'{pid_parent}'")

    # Get de start_and_stop process pid
    pid_start_and_stop = get_pid_of_script("start_and_stop.py")

    print(f"pid_start_and_stop : '{pid_start_and_stop}'")

    # If the program was started by start_and_stop.py, it will :
    # - Send a signal to the start_and_stop program to indicate that reception.py is ready.
    # - Send a monitoring message to the db to indicate program started up
    if pid_parent == pid_start_and_stop:
        local.monitor_system_start_stop(datetime_now, 1)
        os.kill(pid_start_and_stop, signal.SIGTERM)
        print("signal sent")
    else:
        print("Monitor observation started")
        local.monitor_observation_start_stop(datetime_now, 1)
        print("FIN Monitor observation started")

    thread_availability = threading.Thread(target=local_mqtt.check_availability)
    thread_availability.start()

    print("CREATION HANDLER")
    # Wait for a signal comming from start_and_stop program
    signal.signal(signal.SIGUSR1, handler_program_stop)
    signal.signal(signal.SIGUSR2, handler_program_stop)
    print("LOOP")
    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    coordinator.loop_forever()
