import paho.mqtt.client as mqtt
import time
import json

## Constant for the broker port
BROKER_PORT = 1883
## Constant for the broker addr
BROKER_ADDR = "127.0.0.1"


def connect_to_mqtt_broker(client):
    """!
    Create a connection to mqtt broker

    @param client : The mqtt client

    @returns: None
    """
    try:
        client.connect(BROKER_ADDR, BROKER_PORT)
    except Exception as e:
        time.sleep(1)
        # Loop until the connection works
        connect_to_mqtt_broker(client)


def get_all_sensors_on_zigbee2mqtt(details_wanted):
    """!
    Gets all sensors that are paired with Zigbee2Mqtt 

    @param details_wanted: The details needed by the user. 
    all : everything will be included in the sensors_list (will be usable to know the limits of a 
    sensor)
    fname : Only the friendly names
    ieee : Only the ieee address
    label : only the label of the sensor

    @return sensors_list: The list of sensors currently paired with Zigbee2Mqtt
    """

    connected_sensors_list = []

    # Database of every type of sensors available. Their names are obtained in the MQTT Message
    # It is also possible to get this information on the Zigbee2Mqtt website, in the description 
    # field of the corresponding device

    ## TODO A IMPORTER D'UN FICHIER GLOBAL PLUS TARD
    type_of_sensor_list = [
        "Aqara T1 wireless mini switch", "Aqara T1 door & window contact sensor",
        "Aqara P1 human body movement and illuminance sensor", "Vibration sensor",
        "Aqara vibration sensor"
    ]

    # This function is called when a message is received. Because we subscribe to the
    # zigbee2mqtt/bridge/devices topic, a message is immediately received. 
    # When the function is called, it will display all of the sensors currently connected to Zigbee2Mqtt 
    # Whenever a change is made, the new or deleted sensor will be printed.

    def on_message(client, userdata, msg):
        """!
        Function that is called when a message is received from a topic
        In that case, it is zigbee2mqtt/bridge/devices

        @param client: Client
        @param userdata: Unused
        @param msg: JSON message, which contains all of the informations of the sensors

        @return None
        """
        sensors_data = json.loads(msg.payload.decode())

        match details_wanted:

            case "all":
                for sensor in sensors_data:
                    if sensor.get("definition"):
                        sensor_details = {
                            'name': sensor.get('friendly_name', 'Unknown'),
                            'ieee_address': sensor.get('ieee_address', 'Unknown'),
                            'label': sensor.get("definition", {}).get("description", "Unknown")
                        }
                        connected_sensors_list.append(sensor_details)

            case "fname":
                for sensor in sensors_data:
                    if sensor.get("definition"):
                        sensor_details = {
                            'name': sensor.get('friendly_name', 'Unknown')
                        }
                        connected_sensors_list.append(sensor_details)

            case "ieee":
                for sensor in sensors_data:
                    if sensor.get("definition"):
                        sensor_details = {
                            'ieee_address': sensor.get('ieee_address', 'Unknown')
                        }
                        connected_sensors_list.append(sensor_details)

            case "label":
                for sensor in sensors_data:
                    if sensor.get("definition"):
                        sensor_details = {
                            'label': sensor.get("definition", {}).get("description", "Unknown")
                        }
                        connected_sensors_list.append(sensor_details)

        client.loop_stop()
        client.disconnect()

    # Connection to the MQTT CLient
    client = mqtt.Client("Coordinator")
    client.on_message = on_message
    connect_to_mqtt_broker(client)

    # Subscription to the appropriate topic
    client.subscribe("zigbee2mqtt/bridge/devices")

    client.loop_forever()
    return connected_sensors_list


def change_permit_join(state_wanted):
    """!
    Changes the permit_join parameter, which allows zigbee2mqtt to search for new sensors

    @param state_wanted


    @return transmission_state: if the change was correctly made
    """
    transmission_state = ""

    def on_message(client, userdata, msg):
        """!
        Function that is called when a message is received from a topic
        In that case, it is zigbee2mqtt/bridge/response/permit_join

        @param client: Client
        @param userdata: Unused
        @param msg: JSON message, which contains the information whether the change was done

        @return None
        """
        message = str(msg.payload)

        if "ok" in message:
            if "false" in message:
                transmission_state = "L'appairage de capteurs est desactive"
            elif "true" in message:
                transmission_state = "L'appairage de capteurs est active"
            else:
                transmission_state = "Il y a eu une erreur"
        elif "error" in message:
            transmission_state = "Il y a eu une erreur"
        client.disconnect()
        client.loop_stop()

    client = mqtt.Client("Coordinator")
    client.on_message = on_message
    connect_to_mqtt_broker(client)

    # Subscription to the appropriate topic
    client.subscribe("zigbee2mqtt/bridge/response/permit_join")

    # Publish the MQTT message
    client.publish("zigbee2mqtt/bridge/request/permit_join", state_wanted)

    client.loop_forever()

    return transmission_state

def rename_sensor(previous_name, new_name):
    """!
    Function that is called when a sensor is renamed on Zigbee2MQTT

    @param mqtt_msg: The MQTT message received.
    @param new_name: The new name of the sensor

    @return transmission_state: If the rename was correctly done, if not the cause of what happened
    """
    transmission_state = ""

    # This function allows the user to rename a sensor, using the currently known firendly name (or
    # the IEEE address) and the new name
    # This function is called when a message is received.
    # We subscribe to the topic zigbee2mqtt/bridge/response/device/rename, in order to
    # confirm that the rename was done correctly

    def on_message(client, userdata, msg):
        """!
        Function that is called when a message is received from a topic
        In that case, it is zigbee2mqtt/bridge/response/device/rename

        @param client: Client
        @param userdata: Unused
        @param msg: JSON message, which contains the information whether the rename was done

        @return None
        """

        message = str(msg.payload)

        if '"status":"error"' in message:
            if "does not exist" in message:
                transmission_state = "Le nom precedent (ou l'adresse IEEE) n'existe pas."
            elif "is already in use" in message:
                transmission_state = "Un capteur dans le systeme a deja ce nom"
        elif '"status":"ok"':
            transmission_state = "Le capteur a ete renomme correctement."

        client.disconnect()
        client.loop_stop()

    client = mqtt.Client("Coordinator")
    client.on_message = on_message
    connect_to_mqtt_broker(client)

    if new_name != previous_name:
        # Conversion of the message
        message = json.dumps({"from": previous_name, "to": new_name})

        # Subscription to the response topic in order to know how the message was received
        client.subscribe("zigbee2mqtt/bridge/response/device/rename")

        # The message is then published on the appropriate topic
        client.publish("zigbee2mqtt/bridge/request/device/rename", message)

        client.loop_forever()
    else:
        transmission_state = "OK"

    return transmission_state

def get_sensor_value(sensor_friendly_name, label_widget):
    """!
    @brief Get the sensor value of the sensor_friendly_name

    @param sensor_friendly_name : The friendly name of the sensor we want to get the value

    @return The string value if the sensor 
    """
    print("Lancement du thread pour capteur", sensor_friendly_name)
    # The value of the sensor to return
    value=""

    def on_message(client, userdata, msg):
        nonlocal value
        ## The sensor type extracted from the mqtt topic (Topic : zigbee2mqtt/sensor_type/sensor_name)
        sensor_type = msg.topic.split('/')[1]
        ## The sensor name extracted from the mqtt topic (Topic : zigbee2mqtt/sensor_type/sensor_name)
        sensor_label = msg.topic.split('/')[2]
        ## The datas sended by the sensor extracted from the mqtt message in json format
        sensor_datas = json.loads(msg.payload)
        print("Sensor type : ",sensor_type)
        print("Reception message ", sensor_friendly_name)

        match sensor_type:
            case "button":
                if 'action' in sensor_datas:
                    value = "Action : "+str(sensor_datas["action"])
                else:
                    value = "Unknown"
                
            case "door" :
                if 'contact' in sensor_datas:  
                    value = "Contact : "+str(sensor_datas["contact"])
                else:
                    value = "Unknown"

            case "motion" :
                if 'occupancy' in sensor_datas: 
                    value = "Occupancy : "+str(sensor_datas["occupancy"])
                else:
                    value = "Unknown"

            case "vibration" : 
                if 'vibration' in sensor_datas: 
                    value = "Vibration : "+str(sensor_datas["vibration"])
                else:
                    value = "Unknown"

            case _:
                print("The sensor type doesn't match the list")

        if label_widget.winfo_exists():
            label_widget.configure(text=value)
        else:
            client.disconnect()
            client.loop_stop()

    # The mqtt client to collect the data from the broker
    mqtt_client = mqtt.Client("Client"+sensor_friendly_name)

    # The on_message function of the mqtt client
    mqtt_client.on_message = on_message

    # Connection to mqtt broker
    connect_to_mqtt_broker(mqtt_client)

    mqtt_client.subscribe("zigbee2mqtt/"+sensor_friendly_name)

    mqtt_client.loop_forever()


def get_new_sensors():

    sensor_details = {}
    def on_message(client, userdata, msg):
        """!
        Function that is called when a message is received from a topic
        In that case, it is zigbee2mqtt/bridge/devices

        @param client: Client
        @param userdata: Unused
        @param msg: JSON message, which contains all of the informations of the sensors

        @return None
        """
        nonlocal sensor_details
        sensor_data = json.loads(msg.payload.decode())

        if sensor_data.get('data').get('definition'):
            sensor_details = {
                'name': sensor_data.get('data', {}).get('friendly_name', 'Unknown'),
                'ieee_address': sensor_data.get('data', {}).get('ieee_address', 'Unknown'),
                'label': sensor_data.get('data', {}).get('definition', {}).get('description', 'Unknown')
            }
            client.loop_stop()
            client.disconnect()

    # Connection to the MQTT CLient
    client = mqtt.Client("get_new_sensors_client")
    client.on_message = on_message
    connect_to_mqtt_broker(client)

    client.subscribe("zigbee2mqtt/bridge/event")

    client.loop_forever()
    return sensor_details


if __name__ == "__main__":
    print("test")
    print(get_sensor_value("door/door_room"))
    time.sleep(3)
    print(get_sensor_value("door/door_room"))
