"""!
@file start_and_stop.py

@brief This file is the script to start automatically the program when raspberry pi starts
       This script also manage the LED and the shutdown button

@author Naviis-Brain

@version 1.0

@date 31st January 2024
"""
import RPi.GPIO as GPIO
import subprocess
import sys
import os
import time
import signal
import threading

sys.path.append(os.path.abspath('/home/share/PRISMATHOME'))

from utils import system_function
import model.local


# The GPIO pin number of the shutdown button
BUTTON_PIN = 23
# The GPIO pin for the green LED
GREEN_LED_PIN = 17
# The GPIO pin for the yellow LED
YELLOW_LED_PIN = 27
# The GPIO pin for the fan
FAN_PIN = 22
# Global variable to interrupt the yellow_led_blink function
program_up = False
# Global variable to shut down the system
program_down = False
# Global flag to indicate the system as detected a button pressed for shutdown
flag_shut_down = False


def handler_prgm_started(signum, frame):
    """!
    Wait for the signal SIGTERM coming from prism@home program when it is started


    @param signum : The signal number.
    @param frame : The current stack frame.

    @return None
    """
    global program_up
    if signum == signal.SIGTERM:
        program_up = True
    else:
        set_LED_to_green()


def handler_prgm_stopped(signum, frame):
    """!
    Wait for the signal SIGTERM coming from prism@home program when it is stopped

    @param signum : The signal number.
    @param frame : The current stack frame.

    @return None
    """
    global program_down
    if signum == signal.SIGTERM:
        program_down = True
    else:
        set_LED_to_yellow()


def init_GPIO_pins():
    """!
    Initialise the GPIO pins used for the LED. Set mode in output

    @return None
    """
    # Setting selection mode for GPIO in BCM
    GPIO.setmode(GPIO.BCM)

    # Setting the GPIO for the button in INPUT mode.
    # Setting the default value at UP
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Setting pins in output mode
    GPIO.setup(YELLOW_LED_PIN, GPIO.OUT)
    GPIO.setup(GREEN_LED_PIN, GPIO.OUT)
    GPIO.setup(FAN_PIN, GPIO.OUT)


def listen_for_shutdown():
    """!
    Wait for the button pressed event on the box.

    @return None
    """
    global flag_shut_down
    # Wait for a falling event
    # (When the button is pressed the GPIO pin is shorted to ground)
    GPIO.wait_for_edge(BUTTON_PIN, GPIO.FALLING)
    flag_shut_down = True


def yellow_led_blink_start():
    """!
    Make the yellow LED blink until the prism@home program is ready

    @return None
    """
    # Switching off green LED 
    GPIO.output(GREEN_LED_PIN, GPIO.LOW)

    global program_up
    # Make the Yellow LED blink forever
    while not program_up:
        GPIO.output(YELLOW_LED_PIN, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(YELLOW_LED_PIN, GPIO.LOW)
        time.sleep(0.5)


def yellow_led_blink_stop():
    """!
    Make the yellow LED blink forever in background

    @return None
    """
    # Switching off green LED 
    GPIO.output(GREEN_LED_PIN, GPIO.LOW)

    global program_up
    # Make the Yellow LED blink forever
    while True:
        GPIO.output(YELLOW_LED_PIN, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(YELLOW_LED_PIN, GPIO.LOW)
        time.sleep(0.5)


def set_LED_to_green():
    """!
    Set the Bi-color LED to green

    @return None
    """
    GPIO.output(YELLOW_LED_PIN, GPIO.LOW)
    GPIO.output(GREEN_LED_PIN, GPIO.HIGH)


def set_LED_to_yellow():
    """!
    Set the Bi-color LED to yellow

    @return None
    """
    GPIO.output(GREEN_LED_PIN, GPIO.LOW)
    GPIO.output(YELLOW_LED_PIN, GPIO.HIGH)


def switch_fan_ON():
    """!
    Switch on the fan

    @return None
    """
    GPIO.output(FAN_PIN, GPIO.HIGH)


if __name__ == "__main__":

    # Initialise the GPIO pins
    init_GPIO_pins()

    switch_fan_ON()

    thread_yellow_led_blink_start = threading.Thread(target=yellow_led_blink_start)
    thread_yellow_led_blink_start.start()

    model.local.connect_to_local_db()

    id_observation = model.local.get_active_observation()

    arguments = []

    if (id_observation is not None
            and id_observation is not False):

        # Set the signal handler
        signal.signal(signal.SIGTERM, handler_prgm_started)
        sensor_list = model.local.get_sensors_from_observation(id_observation)

        for sensor in sensor_list:
            arguments.append(sensor["type"] + "/" + sensor["label"])

        command = ["python", "/home/share/PRISMATHOME/reception.py"] + arguments

        # Start the main program
        subprocess.Popen(command)
        thread_yellow_led_blink_start.join()
        set_LED_to_green()
    else:

        program_up = True
        thread_yellow_led_blink_start.join()
        set_LED_to_yellow()

    signal.signal(signal.SIGUSR1, handler_prgm_started)
    signal.signal(signal.SIGUSR2, handler_prgm_stopped)

    # TODO : Le retirer une fois la gestion RTC faite dans start_and_stop.sh
    time.sleep(10)

    # Waiting for shutdown button to be pressed
    # Managed in thread to handle the signals while waiting for the button to be pressed
    thread_listen_for_shutdown = threading.Thread(target=listen_for_shutdown)
    thread_listen_for_shutdown.start()

    # listen_for_shutdown()

    while not flag_shut_down:
        time.sleep(1)

    # Creation of a thread
    thread_yellow_led_blink_stop = threading.Thread(target=yellow_led_blink_stop)
    thread_yellow_led_blink_stop.start()

    if model.local.get_active_observation():
        main_pid = system_function.get_pid_of_script("reception.py")

        signal.signal(signal.SIGTERM, handler_prgm_stopped)

        # Send a SIGUSR2 signal to the prism@home program
        system_function.send_signal(main_pid, signal.SIGUSR2)

        # Wait for the signal coming from prism@home program
        while not program_down:
            pass

    # Shutdown the system when everything is ready
    subprocess.run(["sudo", "shutdown", "-h", "now"], check=True)
