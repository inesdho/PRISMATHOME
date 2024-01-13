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
import os
import getpass
import signal
import time
import model.local_mqtt

## Constant for the broker port
BROKER_PORT = 1883
## Constant for the broker addr
BROKER_ADDR = "127.0.0.1"

coordinator = None

pid_start_and_stop = None
pid_parent = None


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
                return parts[1]
    except Exception as e:
        print(f"Erreur lors de la recherche du PID: {e}")
    return None


def handler_prgm_stop(signum, frame):
    """!
    Wait for the signal SIGTERM coming from start_and_stop.py
    when there is a shut-down request. Then close the program.

    @param signum : The signal number.
    @param frame : The current stack frame.

    @return None
    """
    global coordinator, pid_start_and_stop, pid_parent

    # Register the datetime when the signal was received
    datetime_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    # Stop the program
    coordinator.loop_stop()
    coordinator.disconnect()

    # If the signal come from start_and_stop program :
    # Send a monitoring message that the system is shut down
    if pid_parent == pid_start_and_stop:
        local.monitor_system_shut_down_by_participant(datetime_now)

    # Disconnecting from DBs
    local.disconnect_from_local_db()
    remote.disconnect_from_remote_db()

    # Send a signal to start_and_stop program to indicate that the program is closed
    if pid_parent == pid_start_and_stop:
        os.kill(pid_start_and_stop, signal.SIGTERM)


def on_message(client, userdata, msg):
    treatment.data_treatment(client, userdata, msg)


if __name__ == "__main__":

    global coordinator, pid_parent, pid_start_and_stop
    # Connection to local db
    local.connect_to_local_db()

    # Connection to distant db
    remote.connect_to_remote_db()

    ## The mqtt client to collect the data from the broker
    coordinator = mqtt.Client("Coordinator")

    ## The on_message function of the mqtt client
    coordinator.on_message = on_message

    # Connection to mqtt broker
    model.local_mqtt.connect_to_mqtt_broker(coordinator)

    # Subscribe to every sensor paired
    for i in range(len(sys.argv) - 1):
        print("subscribe : zigbee2mqtt/" + sys.argv[i + 1])
        coordinator.subscribe("zigbee2mqtt/" + sys.argv[i + 1])

    # Get the parent process pid
    pid_parent = os.getppid()

    # Get de start_and_stop process pid
    pid_start_and_stop = get_pid_of_script("start_and_stop.py")

    # If the program was started by start_and_stop.py, it will :
    # - Send a signal to the start_and_stop program to indicate that reception.py is ready.
    # - Send a monitoring message to the db to indicate program started up
    if pid_parent == pid_start_and_stop:
        local.monitor_system_started_up_by_participant(datetime_now)
        os.kill(pid_start_and_stop, signal.SIGTERM)

    # Wait for a signal comming from start_and_stop program
    signal.signal(signal.SIGTERM, handler_program_stop)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    coordinator.loop_forever()
