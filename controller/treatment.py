"""!
@file treatment.py

@brief This file is used to treat the information received by the sensor

@author Naviis-Brain

@version 1.0

@date 28th Decembre 2023
"""
import json
from model import local
from datetime import datetime


def data_treatment(client, userdata, mqtt_msg):
    """!
    Callback function triggered upon receiving a PUBLISH message from the server.
    Treats the incoming MQTT message from sensors and call local.py
    to store the data received

    @param mqtt_msg: The MQTT message received.

    @return None
    """

    ## The sensor type extracted from the mqtt topic (Topic : zigbee2mqtt/sensor_type/sensor_name)
    sensor_type = mqtt_msg.topic.split('/')[1]

    ## The sensor name extracted from the mqtt topic (Topic : zigbee2mqtt/sensor_type/sensor_name)
    sensor_label = mqtt_msg.topic.split('/')[2]

    ## The datas sended by the sensor extracted from the mqtt message in json format
    sensor_datas = json.loads(mqtt_msg.payload)

    ## The current time when the data is received formated to timestamp
    datetime_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    ## The id of the sensor that sent datas
    sensor_id = local.get_sensor_from_type_label(sensor_type, sensor_label)

    # Selection of the process to execute according to the sensor
    match sensor_type:

        case "Button":

            if 'action' in sensor_datas:
                # Transform the data in INT
                match sensor_datas["action"]:

                    case "single":
                        temp = 1

                    case "double":
                        temp = 2

                    case "triple":
                        temp = 3

                    case "quadruple":
                        # This case doesn't exit in current zigbee2MQTT version
                        temp = 4

                    case "quintuple":
                        temp = 5

                    case "hold":
                        temp = 6

                    case "release":
                        temp = 7

                    case "many":
                        temp = 8

                    case _:
                        # Something wrong append
                        return

                # Save the data in the db
                print("Enregistrement de la donnée")
                local.save_sensor_data(sensor_id, temp, datetime_now)
                print("Donnée enregistreée")

                if sensor_datas["battery"]:
                    # Update the sensor battery in db
                    print("Mise à jour battery")
                    local.save_sensor_battery(sensor_id, sensor_datas["battery"], datetime_now)
                    print("Fin mise à jour battery")
                print("FIN TRAITEMENT DONNEe")
        case "Door":
            print("Un capteur a envoyé des données")
            if 'contact' in sensor_datas:
                # Save the data in the db
                print("Enregistrement de la donnée")
                local.save_sensor_data(sensor_id, sensor_datas["contact"], datetime_now)
                print("Donnée enregistreée")
                if sensor_datas["battery"]:
                    # Update the sensor battery in db
                    print("Mise à jour battery")
                    local.save_sensor_battery(sensor_id, sensor_datas["battery"], datetime_now)
                    print("Fin mise à jour battery")
                print("FIN TRAITEMENT DONNEe")

        case "Motion":
            print("Un capteur a envoyé des données")
            if 'occupancy' in sensor_datas:
                # Save the data in the db
                local.save_sensor_data(sensor_id, sensor_datas["occupancy"], datetime_now)
                if sensor_datas["battery"]:
                    # Update the sensor battery in db
                    local.save_sensor_battery(sensor_id, sensor_datas["battery"], datetime_now)

        case "Vibration":
            print("Un capteur de vibration a envoyé des datas")
            if 'vibration' in sensor_datas:
                # Save the data in the db
                local.save_sensor_data(sensor_id, sensor_datas["vibration"], datetime_now)
                if sensor_datas["battery"]:
                    # Update the sensor battery in db
                    local.save_sensor_battery(sensor_id, sensor_datas["battery"], datetime_now)

        case _:
            print("The sensor type doesn't match the list")
