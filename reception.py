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
import globals

## Constant for the broker port
BROKER_PORT = 1883
## Constant for the broker addr
BROKER_ADDR = "127.0.0.1"
## The pid of the program which started reception.py
pid_parent = None
## The pid of start_and_stop.py program
pid_start_and_stop = None
## The mqtt client to collect the data from the broker
coordinator = None

def handler_program_stop(signum, frame):
    """!
    Wait for the signal SIGTERM coming from start_and_stop.py
    when there is a shut-down request. Then close the program.

    @param signum : The signal number.
    @param frame : The current stack frame.

    @return None
    """
    global pid_parent, pid_start_and_stop, coordinator

    # Stop availability thread
    local_mqtt.check_availability_stop = True

    # Stop the program
    coordinator.loop_stop()
    coordinator.disconnect()

    # Get the pid of start_and_stop.py program
    pid_start_and_stop = system_function.get_pid_of_script("start_and_stop.py")

    # Register the datetime when the signal was received
    datetime_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    # If the signal come from start_and_stop program (SIGUSR2) :
    if signum == signal.SIGUSR2:
        # Send a monitoring message that the system is shut down
        local.monitor_system_start_stop(datetime_now, 0)
        # Send a signal to start_and_stop program to indicate that the program is closed
        system_function.send_signal(pid_start_and_stop, signal.SIGTERM)
    else:
        # Send a monitoring message that the observation is stopped
        local.monitor_observation_start_stop(datetime_now, 0)

    # Reset the observation mode bit
    globals.global_observation_mode = 0


def on_message(client, userdata, msg):
    treatment.data_treatment(client, userdata, msg)


if __name__ == "__main__":

    # Connection to local db
    local.connect_to_local_db()

    # Set the observation mode by getting it
    globals.global_observation_mode = local.get_observation_mode()

    # Connect to remote db. With a thread in order not to block the program
    connection_thread = threading.Thread(target=remote.connect_to_remote_db)
    connection_thread.start()

    # Create the mqtt client
    coordinator = mqtt.Client("Coordinator")

    # Set the message handling function
    coordinator.on_message = on_message

    # Connection to mqtt broker
    local_mqtt.connect_to_mqtt_broker(coordinator)

    # Subscribe to every sensor paired
    for i in range(len(sys.argv) - 1):
        coordinator.subscribe("zigbee2mqtt/" + sys.argv[i + 1])

    datetime_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    # Get the parent process pid
    pid_parent = os.getppid()

    # Get de start_and_stop process pid
    pid_start_and_stop = system_function.get_pid_of_script("start_and_stop.py")

    # If the program was started by start_and_stop.py, it will :
    # - Send a signal to the start_and_stop program to indicate that reception.py is ready.
    # - Send a monitoring message to the db to indicate program started up
    if pid_parent == pid_start_and_stop:
        # Monitor system started up by participant
        local.monitor_system_start_stop(datetime_now, 1)
        # Send a signal SIGTERM to the start_and_stop program to inform reception.py is up
        system_function.send_signal(pid_start_and_stop, signal.SIGTERM)
    else:
        # Monitor observation started
        local.monitor_observation_start_stop(datetime_now, 1)

    # Start the thread which check the sensors availability
    thread_availability = threading.Thread(target=local_mqtt.check_availability)
    thread_availability.start()

    # Create a signal handler for signal coming from the main.py program
    signal.signal(signal.SIGUSR1, handler_program_stop)

    # Create a signal handler for signal coming from start_and_stop program
    signal.signal(signal.SIGUSR2, handler_program_stop)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    coordinator.loop_forever()
