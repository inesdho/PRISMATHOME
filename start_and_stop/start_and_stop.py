"""!
@file start_and_stop.py

@brief This file is the script to start automaticly the program when raspberry pi starts
       This script also manage the LED and the shutdown button

@author Naviis-Brain

@version 1.0

@date 28th Decembre 2023
"""
import RPi.GPIO as GPIO
import subprocess
import sys
import os
import time
import signal
import threading

sys.path.append(os.path.abspath('/home/share/PRISMATHOME'))

from system import system_function
import model.local

## The GPIO pin number of the shutdown button
BUTTON_PIN = 3
## The GPIO pin for the green LED
GREEN_LED_PIN = 17
## The GPIO pin for the yellow LED
YELLOW_LED_PIN = 27
## Global variable to interrupt the yellow_led_blink function
program_up = False
## Global variable to shutdown the system
program_down = False


def handler_prgm_started(signum, frame):
    """!
    Wait for the signal SIGTERM coming from prism@home program when it is started


    @param signum : The signal number.
    @param frame : The current stack frame.

    @return None
    """
    global program_up
    program_up = True


def handler_prgm_stopped(signum, frame):
    """!
    Wait for the signal SIGTERM coming from prism@home program when it is stopped

    @param signum : The signal number.
    @param frame : The current stack frame.

    @return None
    """
    global program_down
    program_down = True


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


def listen_for_shutdown():
    """!
    Wait for the button pressed event on the box.

    @return None
    """
    # Wait for a falling event
    # (When the button is pressed the GPIO pin is shorted to ground)
    GPIO.wait_for_edge(BUTTON_PIN, GPIO.FALLING)


def yellow_led_blink_start():
    """!
    Make the yellow LED blink until the prism@home program is ready

    @return None
    """
    # Switching off green LED 
    GPIO.output(GREEN_LED_PIN, GPIO.LOW)
    print("Clignotage en cours")

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
    print("Clignotage en cours")

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
    print("GREEN LED")
    GPIO.output(YELLOW_LED_PIN, GPIO.LOW)
    GPIO.output(GREEN_LED_PIN, GPIO.HIGH)


if __name__ == "__main__":

    # Initialise the GPIO pins
    init_GPIO_pins()

    # TODO : Faire clignoter la led ici
    thread_yellow_led_blink_start = threading.Thread(target=yellow_led_blink_start)
    thread_yellow_led_blink_start.start()

    model.local.connect_to_local_db()

    id_observation = model.local.get_active_observation()

    print("start_and_stop : id_observation : ", id_observation)

    arguments = []

    if (id_observation is not None
            and id_observation is not False):
        # Set the signal handler
        signal.signal(signal.SIGTERM, handler_prgm_started)
        sensor_list = model.local.get_sensors_from_observation(id_observation)
        print("sensor list: ", sensor_list)
        for sensor in sensor_list:
            arguments.append(sensor["type"] + "/" + sensor["label"])

        print("arguments : ", arguments)
        command = ["python", "/home/prisme/Prisme@home/PRISMATHOME/reception.py"] + arguments

        # Start the main program
        subprocess.Popen(command)
    else:
        print("else")
        program_up = True

    thread_yellow_led_blink_start.join()
    print("thread_yellow_led_blink_start joined")

    set_LED_to_green()

    # Waiting for shutdown button to be pressed
    listen_for_shutdown()
    print("listen shut down")

    # Creation of a thread
    thread_yellow_led_blink_stop = threading.Thread(target=yellow_led_blink_stop)
    thread_yellow_led_blink_stop.start()

    if model.local.get_active_observation():
        main_pid = system_function.get_pid_of_script("reception.py")

        print("\033[33mmain_pid : ", main_pid, "\033[0m")

        signal.signal(signal.SIGTERM, handler_prgm_stopped)

        # Send a SIGUSR2 signal to the prism@home program
        system_function.send_signal(main_pid, "SIGUSR2")

        # Wait for the signal comming from prism@home program
        while not program_down:
            pass

        print("coucou")
    # Shutdown the system when everything is ready
    subprocess.run(["sudo", "shutdown", "-h", "now"], check=True)
