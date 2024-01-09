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

    @param details_wanted: The details needed by the user : all, fname, ieee or label.
    all : everything will be included in the connected_sensors_list (fname, ieee and label)
    fname : Only the friendly names
    ieee : Only the ieee address
    label : only the label of the sensor

    @return sensors_list: The list of sensors currently paired with Zigbee2Mqtt
    """

    # The list of sensors to return
    connected_sensors_list = []

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
    client = mqtt.Client("get_all_sensors_on_zigbee2mqtt")
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
    transmission_state = 0

    def on_message(client, userdata, msg):
        """!
        Function that is called when a message is received from a topic
        In that case, it is zigbee2mqtt/bridge/response/permit_join

        @param client: Client
        @param userdata: Unused
        @param msg: JSON message, which contains the information whether the change was done

        @return None
        """
        nonlocal transmission_state
        message = str(msg.payload)

        if "ok" in message:
            transmission_state = 1
        elif "error" in message:
            transmission_state = 0
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
            # 1 : The rename was correctly done
            # 2 : Targeted sensor does not exist
            # 3 : Unknown
    """
    transmission_state = 3
    cpt=0

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


        nonlocal transmission_state
        nonlocal cpt

        # Do not execute twice the on_message function to avoid problem with the recursive call
        if cpt == 0:
            cpt = 1
        else:
            print("coucou")
            return

        # Convert the feedback in json
        rename_feedback = json.loads(msg.payload)
        print("feeedback: ", rename_feedback)
        if 'ok' in rename_feedback["status"]:
            transmission_state = 1
        elif 'error' in rename_feedback:
            if 'does not exist' in rename_feedback['error']:
                transmission_state = 2
            elif 'is already in use' in rename_feedback['error']:
                # Get the list of sensors
                sensors = get_all_sensors_on_zigbee2mqtt("all")

                for device in sensors:
                    # Seek for the sensor which use the name we want
                    if device["name"] == new_name:
                        # Rename the sensor with his ieee_addres + x
                        rename_sensor(new_name, device["ieee_address"] + "x")
                        break
                # Call the function again to rename the sensor now that new_name is not used
                transmission_state = rename_sensor(previous_name, new_name)

            else:
                print("WTF 1 : ",rename_feedback)
                transmission_state = 3
        else:
            print("WTF 2 : ", rename_feedback)
            transmission_state = 3

        client.disconnect()
        client.loop_stop()

    # Connection to the MQTT Client
    client = mqtt.Client("Coordinator")
    client.on_message = on_message
    connect_to_mqtt_broker(client)

    # Check if it is the same name, there is no need to rename it
    if new_name == previous_name:
        transmission_state = 1
        client.disconnect()
        client.loop_stop()
    else:
        # Conversion of the message
        message = json.dumps({"from": previous_name, "to": new_name})

        # Subscription to the response topic in order to know how the message was received
        client.subscribe("zigbee2mqtt/bridge/response/device/rename")

        # The message is then published on the appropriate topic
        client.publish("zigbee2mqtt/bridge/request/device/rename", message)

    client.loop_forever()
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
            case "Button":
                if 'action' in sensor_datas:
                    value = "Action : "+str(sensor_datas["action"])
                else:
                    value = "Unknown"
                
            case "Door" :
                if 'contact' in sensor_datas:  
                    value = "Contact : "+str(sensor_datas["contact"])
                else:
                    value = "Unknown"

            case "Motion" :
                if 'occupancy' in sensor_datas: 
                    value = "Occupancy : "+str(sensor_datas["occupancy"])
                else:
                    value = "Unknown"

            case "Vibration" :
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
    mqtt_client = mqtt.Client("get_sensor_value"+sensor_friendly_name)

    # The on_message function of the mqtt client
    mqtt_client.on_message = on_message

    # Connection to mqtt broker
    connect_to_mqtt_broker(mqtt_client)

    mqtt_client.subscribe("zigbee2mqtt/"+sensor_friendly_name)

    mqtt_client.loop_forever()

def get_new_sensors():
    """!
    This function is used to get the new sensors that joined zigbee2mqtt after a permit join

    @param client: Client
    @param userdata: Unused
    @param msg: Message from topic

    @return None
    """
    sensor_details = {}
    def on_message(client, userdata, msg):
        """!
        Function that is called when a message is received from a topic
        In that case, it is zigbee2mqtt/bridge/event

        @param client: Client
        @param userdata: Unused
        @param msg: Message from topic

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

    # Connection to the MQTT Client
    client = mqtt.Client("get_new_sensors")
    client.on_message = on_message
    connect_to_mqtt_broker(client)

    client.subscribe("zigbee2mqtt/bridge/event")

    client.loop_forever()
    return sensor_details
