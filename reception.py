"""!
@mainpage Prisme@home project documentation

@section description_main Description
This project has been realized in the frame of a end of study project.

@section notes_main Notes
Project realized by 5 students from IG2I.

@file main.py

@brief This is the main project file for collecting the informations with the sensors.
        In this file we create the mqtt client and subscribe to the sensors we need.

@author Naviis-Brain

@version 1.0

@date 6th Decembre 2023
"""
import paho.mqtt.client as mqtt
import sys
import controller.treatment as treatment

def on_connect(client, userdata, flags, rc):
    """!
    Callback function triggered upon connection to the MQTT broker.

    @param client: The client instance that triggered this callback.
    @param userdata: User data of any type that was set in the client object.
    @param flags: Response flags sent by the broker.
    @param rc: The connection result code.

    @returns: None
    """
    print("Connected with result code "+str(rc))


def on_message(client, userdata, msg):
    """!
    Callback function triggered upon receiving a PUBLISH message from the server.

    @param client: The client instance that triggered this callback.
    @param userdata: User data of any type that was set in the client object.
    @param msg: The received message.

    @returns: None
    """

    treatment.treat(msg)


treatment.local.db = treatment.local.mysql.connector.connect(
    host="localhost",
    user="root",
    password="Q3fhllj2",
    database="prisme@home_test"
)

treatment.local.cursor = treatment.local.db.cursor();

## The mqtt client to collect the data from the broker
coordinator = mqtt.Client("Coordinator")
## The on_connect function of the mqtt client
coordinator.on_connect = on_connect
## The on_message function of the mqtt client
coordinator.on_message = on_message

coordinator.connect("127.0.0.1", 1883)

for i in range(len(sys.argv)-1):
    coordinator.subscribe("zigbee2mqtt/"+sys.argv[i+1])

    

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
coordinator.loop_forever()

db.close();