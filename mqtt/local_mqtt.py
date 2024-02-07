import paho.mqtt.client as mqtt
import time
import json
from utils import globals
from datetime import datetime
from model import local

## Constant for the broker port
BROKER_PORT = 1883
## Constant for the broker addr
BROKER_ADDR = "127.0.0.1"

check_availability_stop = False


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
        # Ending the function when the informations are retrieved
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

        # Checks the value of the payload
        if "ok" in message:
            transmission_state = 1
        elif "error" in message:
            transmission_state = 0

        # Ending the function when the information are retrieved
        client.disconnect()
        client.loop_stop()

    # Connection to the MQTT Client
    client = mqtt.Client("change_permit_join")
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
    cpt = 0

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
            return

        # Convert the feedback in json
        rename_feedback = json.loads(msg.payload)

        # Check the feedback
        if 'ok' in rename_feedback["status"]:
            transmission_state = 1
        elif 'error' in rename_feedback:

            # Case where the previous name doesn't match anything
            if 'does not exist' in rename_feedback['error']:
                transmission_state = 2

            # Case where the new_name is already bound to another sensor
            # It can also mean that the new_name is the same as the previous name,
            # but we already handle that case in the program so it nerver happens.
            #
            # In that case, instead of showing the error (which can be confusing for the user),
            # we rename the sensor correctly, and rename the sensor that had the name to its
            # IEEE address + x
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
                transmission_state = 3
        else:
            transmission_state = 3

        # Ending the function
        client.disconnect()
        client.loop_stop()

    # Connection to the MQTT Client
    client = mqtt.Client("rename_sensor"+previous_name)
    client.on_message = on_message
    connect_to_mqtt_broker(client)

    # Check if it is the same name, there is no need to rename it
    if new_name == previous_name:
        transmission_state = 1

        # Ending the function
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
    global thread_done
    # The value of the sensor to return
    value = ""
    print("Getting the sensor value")

    def on_message(client, userdata, msg):
        nonlocal value
        ## The sensor type extracted from the mqtt topic (Topic : zigbee2mqtt/sensor_type/sensor_name)
        sensor_type = msg.topic.split('/')[1]
        ## The sensor name extracted from the mqtt topic (Topic : zigbee2mqtt/sensor_type/sensor_name)
        sensor_label = msg.topic.split('/')[2]
        ## The datas sended by the sensor extracted from the mqtt message in json format
        sensor_datas = json.loads(msg.payload)

        print("Value getted")

        match sensor_type:
            case "Button":
                if 'action' in sensor_datas:
                    value = "Action : " + str(sensor_datas["action"])
                else:
                    value = "Unknown"

            case "Door":
                if 'contact' in sensor_datas:
                    value = "Contact : " + str(sensor_datas["contact"])
                else:
                    value = "Unknown"

            case "Motion":
                if 'occupancy' in sensor_datas:
                    value = "Occupancy : " + str(sensor_datas["occupancy"])
                else:
                    value = "Unknown"

            case "Vibration":
                if 'vibration' in sensor_datas:
                    value = "Vibration : " + str(sensor_datas["vibration"])
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
    mqtt_client = mqtt.Client("get_sensor_value" + sensor_friendly_name)

    # The on_message function of the mqtt client
    mqtt_client.on_message = on_message

    # Connection to mqtt broker
    connect_to_mqtt_broker(mqtt_client)

    mqtt_client.subscribe("zigbee2mqtt/" + sensor_friendly_name)

    mqtt_client.loop_start()

    while not globals.thread_done:
        time.sleep(1)

    mqtt_client.loop_stop()
    mqtt_client.disconnect()


def get_new_sensors(flag):
    """!
    This function is used to get the new sensors that joined zigbee2mqtt after a permit join

    @param None

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
        print("sensor datas : ", sensor_data)

        if sensor_data.get('data').get('definition'):
            print("Adding details")
            sensor_details = {
                'name': sensor_data.get('data', {}).get('friendly_name', 'Unknown'),
                'ieee_address': sensor_data.get('data', {}).get('ieee_address', 'Unknown'),
                'label': sensor_data.get('data', {}).get('definition', {}).get('description', 'Unknown')
            }
            # Ending the function
            client.loop_stop()
            client.disconnect()
            flag[0]=True

    # Connection to the MQTT Client
    client = mqtt.Client("get_new_sensors")
    client.on_message = on_message
    connect_to_mqtt_broker(client)

    # Subscribing to the topic
    client.subscribe("zigbee2mqtt/bridge/event")

    client.loop_start()

    while not flag[0]:
        time.sleep(1)

    flag[0] = False

    print("return details")
    return sensor_details


def check_availability():
    """!
    This function will detect all the sensors paired with ZigBee2MQTT. Gathered information
    will be then sent to the user

    @return nothing
    """

    ##  Double list, which contains the sensors and their status
    availabilities = [
        ["Sensor"],
        ["Status"],
    ]

    ## The topic list we need to subcribe to
    list_of_topics = []

    def on_message_getall(client, userdata, msg):
        """!
        Function that is called when a message is received from a topic
        In that case, it is zigbee2mqtt/bridge/devices
        It will gather all the devices and subscribe to the availability fields corresponding

        @param client: Client
        @param userdata: Unused
        @param msg: JSON message, which contains all the information of the sensors

        @return None
        """

        nonlocal availabilities
        nonlocal list_of_topics
        # Gets all the sensor connected in the system
        connected_devices = get_all_sensors_on_zigbee2mqtt("fname")

        for i in range(len(connected_devices)):

            # Only getting the friendly names
            fname = str(connected_devices[i].get('name', 'Unknown'))
            # Checks if the sensor already exists
            if not fname in availabilities[0]:

                # Subscribing to the topic
                topic = "zigbee2mqtt/" + fname + "/availability"
                client.subscribe(topic)

                # Only happens on the first iteration
                if "Sensor" in availabilities[0][0]:
                    availabilities[0][0] = connected_devices[i].get('name', 'Unknown')
                    availabilities[1][0] = 'none'

                # Happens every time, except for the first iteration
                else:
                    # Inserts the name of the sensor in the list, and also the temporary "none" state
                    availabilities[0].insert(i, connected_devices[i].get('name', 'Unknown'))
                    availabilities[1].insert(i, 'none')

                # Adding the topic to the list
                list_of_topics.insert(i, topic)

    def on_message(client, userdata, msg):
        """!
        Function that is called when a message is received from a topic
        In that case, it is zigbee2mqtt/FRIENDLY_NAME/availability
        The FRIENDLY_NAME is the name of the sensor coming from the on_message_getall function

        @param client: Client
        @param userdata: Unused
        @param msg: JSON message, which contains all of the informations of the sensors

        @return None
        """
        nonlocal availabilities
        nonlocal list_of_topics

        # Checks if the payload is empty or not. Can happen only when a sensor is renamed
        if not "b''" in str(msg.payload):

            # Gets the message received
            availability_message = json.loads(msg.payload.decode())

            # Searching for every sensor connected
            for i in range(len(list_of_topics)):

                # Checks which index is corresponding
                fname = msg.topic.replace('zigbee2mqtt/', '').replace('/availability', '')

                # Divides the friendly name to send data to the database
                data_to_database = fname.split("/")
                if len(data_to_database) < 2:
                    return

                datetime_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

                # Tries to find the topic received in the availabilities list
                if fname in availabilities[0][i]:
                    # Case where the state of the new sensor is NOT in the system
                    if 'none' in availabilities[1][i]:

                        # That sensor is online
                        if 'online' in availability_message['state']:
                            availabilities[1][i] = "online"

                        # That sensor is offline
                        elif 'offline' in availability_message['state']:
                            availabilities[1][i] = "offline"
                            sensor_id = local.get_sensor_from_type_label(data_to_database[0], data_to_database[1])
                            if sensor_id:
                                local.monitor_sensor_availability(sensor_id, datetime_now, 0)

                    # Case where the sensor is already in the system
                    elif 'online' in availabilities[1][i]:
                        if 'offline' in availability_message['state']:
                            availabilities[1][i] = "offline"
                            sensor_id = local.get_sensor_from_type_label(data_to_database[0], data_to_database[1])
                            if sensor_id:
                                local.monitor_sensor_availability(sensor_id, datetime_now, 0)

                    elif 'offline' in availabilities[1][i]:
                        if 'online' in availability_message['state']:
                            availabilities[1][i] = "online"
                            sensor_id = local.get_sensor_from_type_label(data_to_database[0], data_to_database[1])
                            if sensor_id:
                                local.monitor_sensor_availability(sensor_id, datetime_now, 1)

    def on_message_rename(client, userdata, msg):
        """!
        Function that is called when a message is received from a topic
        In that case, it is zigbee2mqtt/bridge/response/device/rename
        It is called when a sensor is renamed, which also renames the sensor in availabilities and
        modifies the topics

        @param client: Client
        @param userdata: Unused
        @param msg: JSON message, which contains all of the informations of the sensors

        @return None
        """
        rename_feedback = json.loads(msg.payload)
        found = False

        # Checks if the rename was correctly done
        if 'ok' in rename_feedback['status']:

            # Gets the previous and the new names
            previous_name = rename_feedback.get('data', {}).get('from', 'Unknown')
            new_name = rename_feedback.get('data', {}).get('to', 'Unknown')

            for i in range(len(availabilities[0])):

                # Checks if the sensor has already been found
                if found == False:

                    # Tries to find which sensor has been renamed
                    if previous_name in availabilities[0][i]:
                        # Unsubscribing to the previous topic
                        topic = "zigbee2mqtt/" + previous_name + "/availability"
                        client.unsubscribe(topic)

                        # Subscribing to the new topic
                        topic = "zigbee2mqtt/" + new_name + "/availability"
                        client.subscribe(topic)

                        # Removing the sensor, the state and the topic from the topic list. We don't
                        # need to add the new sensor as this will be done in the on_message_getall
                        # function
                        del (availabilities[0][i])
                        del (availabilities[1][i])
                        del (list_of_topics[i])
                        found = True

    def on_message_remove(client, userdata, msg):
        """!
        Function that is called when a message is received from a topic
        In that case, it is zigbee2mqtt/bridge/response/device/remove
        It will remove the sensor from the availabilites list, and unsubscribe to the topic
        corresponding to it

        @param client: Client
        @param userdata: Unused
        @param msg: JSON message, which contains all of the informations of the sensors

        @return None
        """
        remove_feedback = json.loads(msg.payload)

        # Checks if the remove was correctly done
        if 'ok' in remove_feedback['status']:

            # Gets which sensor was removed
            fname_removed = remove_feedback.get('data', {}).get('id', 'Unknown')

            for i in range(len(availabilities)):

                # Tries to find which sensor has been renamed
                if fname_removed in availabilities[0][i]:
                    # Unsubcribing to the topic
                    topic = "zigbee2mqtt/" + fname_removed + "/availability"
                    client.unsubscribe(topic)

                    # Removing the sensor, the state and the topic from the topic list.
                    del (availabilities[0][i])
                    del (availabilities[1][i])
                    del (list_of_topics[i])

    client = mqtt.Client("get_availability")
    client.on_message = on_message
    connect_to_mqtt_broker(client)

    # Filtering the topics. Messages received on zigbee/bridge/devices will be sent to the
    # on_message_getall function
    client.message_callback_add("zigbee2mqtt/bridge/devices", on_message_getall)

    # When a sensor is renamed
    client.message_callback_add("zigbee2mqtt/bridge/response/device/rename", on_message_rename)

    # When a sensor is removed
    client.message_callback_add("zigbee2mqtt/bridge/response/device/remove", on_message_remove)

    # Subscription to the appropriate topics
    client.subscribe("zigbee2mqtt/bridge/devices")
    client.subscribe("zigbee2mqtt/bridge/response/device/remove")
    client.subscribe("zigbee2mqtt/bridge/response/device/rename")

    client.loop_start()

    while not check_availability_stop:
        time.sleep(1)

    client.loop_stop()
    client.disconnect()
