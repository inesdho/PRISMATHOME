"""!
@file treatment.py

@brief This file is used to treat the information received by the sensor

@author Naviis-Brain

@version 1.0

@date 6th Decembre 2023
"""
import json
import local
from datetime import datetime

def treat(mqtt_msg):
    """!
    Treats the incoming MQTT message from sensors and call local.py to store the data received

    @param mqtt_msg: The MQTT message received.

    @return None
    """

    # The sensor type extracted from the mqtt topic (Topic : zigbee2mqtt/sensor_type/sensor_name)
    sensor_type = mqtt_msg.topic.split('/')[1]
    # The sensor name extracted from the mqtt topic (Topic : zigbee2mqtt/sensor_type/sensor_name)
    sensor_label = mqtt_msg.topic.split('/')[2]
    # The datas sended by the sensor extracted from the mqtt message in json format
    sensor_datas = json.loads(mqtt_msg.payload)
    # The current time when the data is received formated to timestamp
    datetime_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    print("sensor_datas =", sensor_datas)

    sensor_id = local.find_sensor_by_type_label(sensor_type, sensor_label)

    print("Sensor_id = ", sensor_id)

# Selection of the process to execute according to the sensor
    match sensor_type:

        case "button":

            if 'action' in sensor_datas:  
                match sensor_datas["action"]:

                    case "single":
                        temp=1

                    case "double":
                        temp=2

                    case "triple":
                        temp=3

                    case "quintuple":
                        temp=5

                    case "hold":
                        temp=6

                    case "release":
                        temp=0

                    case _:
                        print("Impossible case")
                        temp=7
                        # Impossible case

                local.save_datas(sensor_id, temp, datetime_now)
                if(sensor_datas["battery"]):
                    local.save_sensor_battery(sensor_id, sensor_datas["battery"])
            
        case "door" :
            print("Un capteur a envoyé des données")
            if 'contact' in sensor_datas: 
                local.save_datas(sensor_id, sensor_datas["contact"],datetime_now)
                if(sensor_datas["battery"]):
                    local.save_sensor_battery(sensor_id, sensor_datas["battery"])

        case "motion" :
            print("Un capteur a envoyé des données")
            if 'occupancy' in sensor_datas: 
                local.save_datas(sensor_id, sensor_datas["occupancy"],datetime_now)
                if(sensor_datas["battery"]):
                    local.save_sensor_battery(sensor_id, sensor_datas["battery"])

        case "vibration" : 
            print("Un capteur de vibration a envoyé des datas")
            if 'vibration' in sensor_datas: 
                local.save_datas(sensor_id, sensor_datas["vibration"],datetime_now)
                if(sensor_datas["battery"]):
                    local.save_sensor_battery(sensor_id, sensor_datas["battery"])

        case _:
            print("The sensor type doesn't match the list")



