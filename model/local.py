"""!
@file local.py

@brief This file is used communicate with the database

@author Naviis-Brain - Paul - Matteo

@version 1.1

@date January 10 2024
"""
import errno

import globals

import mysql.connector
import time
import hashlib
import threading

from model import remote

local_db = None
local_cursor = None

local_cursor_protection = threading.Lock()

caching = False


# DONE
def connect_to_local_db():
    """!
    Tries to connect to the local database and loops until successfully connected

    @return None
    """
    global local_db, local_cursor
    try:
        # Connexion to the database
        with local_cursor_protection:
            local_db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Q3fhllj2",
                database="prisme_home_1"
            )
            local_cursor = local_db.cursor()
            print("Connected to local database")
    except Exception as e:
        time.sleep(1)
        # Loop until the connection works
        connect_to_local_db()


# DONE
def get_system_id():
    """!
    Gets the id of the current system from the local database

    @return the system's ID if successful, None otherwise
    """
    global local_db, local_cursor
    try:
        # Check if the local database connection is established
        if local_db is not None and local_db.is_connected():
            query = """SELECT s.id_system FROM system s"""

            with local_cursor_protection:
                local_cursor.execute(query)
                # Fetch the result
                result = local_cursor.fetchone()

            if result:
                return result[0]

        else:
            # If not connected to the local database, attempt to reconnect and retry
            print("get_system_id Error while executing select statement : database is not connected, retrying")
            connect_to_local_db()
            return get_system_id()

    except Exception as e:
        # Handle any exceptions that may occur during the query execution
        print(f"Error getting system id: {e}")

    # Return None if the sensor type is not found or there are errors
    return None


# DONE
def add_system_id(local_id):
    """!
    Prepends the system's ID to any local ID provided in order to store them into the distant database
    @param local_id the local ID to which the system ID needs to be added
    @return the modified ID to be inserted into the distant database
    """
    system_id = get_system_id()
    concat_id = f"syst{system_id}_{local_id}"
    return concat_id


# DONE
def send_query(query_type, table, fields=None, values=None, condition=None):
    """!
    Inserts, updates, or deletes data in the local database and then saves it to the remote database.

    @param query_type : The type of query ("INSERT", "UPDATE", "DELETE", etc.).
    @param table : The name of the table.
    @param fields : List of field names for the query.
    @param values : List of values corresponding to the fields.
    @param condition : Condition for the UPDATE or DELETE query (optional).

    @return 1 if data sent to local and remote DB, 2 if sent only to local DB, 0 if no data was stored
    """
    remote_values = None
    remote_query = None
    valid_query_types = ["INSERT", "UPDATE", "DELETE"]
    if query_type.upper() not in valid_query_types:
        raise ValueError(f"Invalid query_type. Supported types are {', '.join(valid_query_types)}.")

    # Building queries according to their type
    if query_type.upper() == "INSERT":
        if values is None or fields is None:
            raise ValueError(f"Values and fields are required for {query_type} queries.")
        query = f"{query_type} INTO `{table}`"
        query += f" ({', '.join(fields)}) VALUES ({', '.join(['%s'] * len(values))})"

    elif query_type.upper() == "UPDATE":
        if condition is None:
            raise ValueError(f"Condition is required for {query_type} queries.")
        query = f"{query_type} `{table}` SET "
        query += ', '.join([f"{field} = %s" for field in fields])
        query += f" WHERE {condition}"

    elif query_type.upper() == "DELETE":
        if condition is None:
            raise ValueError(f"Condition is required for {query_type} queries.")
        query = f"{query_type} FROM `{table}`"
        query += f" WHERE {condition}"

    print(f"\033[92mTry execute (local) : {query, values}\033[0m")

    try:
        # Storing data in local DB
        with local_cursor_protection:
            local_cursor.execute(query, values)
            local_db.commit()
            last_id = local_cursor.lastrowid

        print(f"\033[92mExecuted (local) : {query, values}\033[0m")

        if query_type.upper() == "INSERT" and table == 'observation':
            globals.global_new_id_observation = last_id

        # Building remote query
        # Appending system id to specific ids before sending to remote DB storing function
        if fields is not None and values is not None:
            remote_values = tuple(add_system_id(value) if field in remote.ids_to_modify
                                  else value for field, value in zip(fields, values))
        # Check if the condition's id needs to be modified
        if condition is not None:
            left, right = map(str.strip, condition.split('='))
            if left in remote.ids_to_modify:
                right = str(add_system_id(right))  # Modifying the id to look for to prepend the system's id
            modified_condition = f"{left} = '{right}'"

        if query_type.upper() == "INSERT" and table in remote.tables_to_prepend:  # Need to add the id in the remote base
            fields = ['id_' + table] + fields
            remote_values = (add_system_id(last_id),) + remote_values
            remote_query = f"{query_type} INTO `{table}`"
            remote_query += f" ({', '.join(fields)}) VALUES ({', '.join(['%s'] * len(fields))})"

        elif query_type.upper() == "INSERT":
            remote_query = f"{query_type} INTO `{table}`"
            remote_query += f" ({', '.join(fields)}) VALUES ({', '.join(['%s'] * len(fields))})"

        elif query_type.upper() == "UPDATE":
            remote_query = f"{query_type} `{table}` SET "
            remote_query += ', '.join([f"{field} = %s" for field in fields])
            remote_query += f" WHERE {modified_condition}"

        elif query_type.upper() == "DELETE":
            remote_query = f"{query_type} FROM `{table}`"
            remote_query += f" WHERE {modified_condition}"
        print(f"\033[94mTry execute (distant) : {remote_query, remote_values}\033[0m")

        # Attempting to send to remote DB
        if remote.execute_remote_query(remote_query, remote_values) == 1:  # Success
            return 1
        else:
            cache_query(remote_query, remote_values)
            return 2
    except mysql.connector.Error as error:
        if error.errno == 2013:
            # CBD: Monitoring "Lost local DB connection at [datetime]"
            connect_to_local_db()
            # CBD: Monitoring "local DB connection at [datetime]"
            return send_query(query_type, table, fields, values, condition)
        else:
            print("\033[91mPB send_query : ", query, values, "\033[0m")
            print("\033[91mError (local):", error, "Code : ", error.errno, "\033[0m")
            return 0


# DONE
def cache_query(remote_query, remote_values):
    """!
    Caches the query that couldn't be sent to the remote database, in the local database as plain text
    @param remote_query: the query to store
    @param remote_values: the values of said query
    """
    print("Début caching : ", remote_query, remote_values)
    global caching
    global local_db, local_cursor
    remote_query_as_text = None
    # Store the remote query in the cache table as plain text
    caching_query = """INSERT INTO `remote_queries` (`query`) VALUES (%s)"""
    # Formatting the query to be saved as a string
    if remote_values is not None:
        remote_values = tuple(repr(value) for value in remote_values)  # transform each element into a representation
        remote_query_as_text = remote_query.format(*remote_values) % remote_values
    else:
        remote_query_as_text = remote_query
    with local_cursor_protection:
        local_cursor.execute(caching_query, (remote_query_as_text,))
        local_db.commit()

    caching = False
    print("Fin caching : ", remote_query, remote_values)


# DONE
def save_sensor_data(sensor_id, data, timestamp):
    """!
    Inserts into the databases (local and remote) the data from the sensor

    @param sensor_id : The ID of the sensor.
    @param data : The data sent by the sensor.
    @param timestamp : The datetime when the data was received

    @return result of the send_query function (1 if data sent to local and remote DB, 2 if sent only to local DB,
    0 if no data was stored
    """
    values = (sensor_id, data, timestamp)
    return send_query('insert', 'data', ['id_sensor', 'data', 'timestamp'], values)


# DONE
def set_battery_low(sensor_id, datetime):
    """!
    Insert the monitoring message "Sensor battery low"

    @param sensor_id: The ID of the sensor.
    @param datetime : The datetime when the datas had been received.

    @return result of the send_query function (1 if data sent to local and remote DB, 2 if sent only to local DB,
    0 if no data was stored
    """
    values = (sensor_id, get_system_id(), datetime, get_error_id_from_label('Sensor battery low'))
    return send_query('insert', 'monitoring', ['id_sensor', 'id_system', 'timestamp', 'id_error'], values)


# DONE
def save_sensor_battery(sensor_id, battery, datetime):
    """!
    Update the battery percentage of a sensor in the database

    @param sensor_id: The ID of the sensor.
    @param battery: The new battery percentage value.
    @param datetime: The timestamp when the data had been received
    @return True if successful, False if not
    """
    values = (battery,)
    condition = 'id_sensor = ' + str(sensor_id)
    if send_query('update', 'sensor', ['battery_percentage'], values, condition) == 0:
        return False

    if battery < 10:
        # update monitoring table
        if set_battery_low(sensor_id, datetime) == 0:
            return False

    return True


# DONE
def get_sensor_type_from_id_type(id_type):
    """!
    Finds the sensor type corresponding to the given id_type in the local database.

    @param id_type: The id_type of the sensor.
    @return: The corresponding sensor type if found, otherwise None.
    """
    global local_db, local_cursor
    try:
        # Check if the local database connection is established
        if local_db is not None and local_db.is_connected():
            query = "SELECT type FROM sensor_type WHERE id_type = %s"

            with local_cursor_protection:
                local_cursor.execute(query, (id_type,))

                # Fetch the result
                result = local_cursor.fetchone()
            if result:
                return result[0]
        else:
            # If not connected to the local database, attempt to reconnect and retry
            print(
                "get_sensor_type_from_id_type Error while executing select statement : database is not connected, retrying")
            connect_to_local_db()
            return get_sensor_type_from_id_type(id_type)

    except Exception as e:
        # Handle any exceptions that may occur during the query execution
        print(f"Error finding sensor type from id_type: {e}")

    # Return None if the sensor type is not found or there are errors
    return None


# DONE
def get_sensor_type_list():
    """!
    Gets all the sensor types and ids in the local database

    @return: The corresponding sensor type if found, otherwise None.
    """
    global local_db, local_cursor
    try:
        # Check if the local database connection is established
        if local_db is not None and local_db.is_connected():
            query = "SELECT id_type, type FROM sensor_type"

            with local_cursor_protection:
                local_cursor.execute(query)

                # Fetch the result
                result = local_cursor.fetchall()
            if result:
                return result
        else:
            # If not connected to the local database, attempt to reconnect and retry
            print("get_sensor_type_list Error while executing select statement : database is not connected, retrying")
            connect_to_local_db()
            return get_sensor_type_list()

    except Exception as e:
        # Handle any exceptions that may occur during the query execution
        print(f"Error finding sensor types : {e}")

    # Return None if no sensor types were found or there are errors
    return None


# DONE
def get_sensor_from_type_label(sensor_type, label):
    """!
    Select in the database the active sensor matching type and label

    @param sensor_type : The sensor type.
    @param label : The sensor label.

    @return The ID of the corresponding sensor, False if no sensor was found or an error occurred
    """
    global local_db, local_cursor

    try:
        if local_db is not None and local_db.is_connected():
            query = """
                SELECT s.id_sensor 
                FROM sensor s 
                JOIN sensor_type st ON s.id_type = st.id_type
                JOIN observation o ON s.id_observation = o.id_observation
                WHERE s.label = %s AND st.type = %s AND o.active = 1;
                """

            values = (label, sensor_type)

            with local_cursor_protection:
                local_cursor.execute(query, values)
                rows = local_cursor.fetchone()
            if rows[0] is not None:
                return rows[0]
            else:
                return False
        else:
            # If not connected to the local database, attempt to reconnect and retry
            print("Error while executing select statement : database is not connected, retrying")
            connect_to_local_db()
            return get_sensor_from_type_label(sensor_type, label)
    except Exception as e:
        # Handle any exceptions that may occur during the query execution
        print(f"Error getting id sensor : {e}")
        return False


# DONE
def get_sensors_from_configuration(id_config):
    """!
    Gets all the sensors associated with the given configuration id in the local database and returns them as a list
    with a special format

    @param id_config: The configuration id
    @return: A list of sensors formatted as such [{"label": "Sensor1","description": "Description1","type": "Type1"},...
    """
    print("Entrée dans la fonction get_sensors_from_configuration")
    global local_db, local_cursor
    try:
        # Check if the local database connection is established
        if local_db is not None and local_db.is_connected():
            query = (
                "SELECT sc.sensor_label, sc.sensor_description, st.type "
                "FROM sensor_config sc, sensor_type st  "
                "WHERE sc.id_config = %s  "
                "AND sc.id_sensor_type = st.id_type")

            with local_cursor_protection:
                print("get_sensors_from_configuration : id_config = " + str(id_config))
                local_cursor.execute(query, (id_config,))

                # Fetch the result
                result = local_cursor.fetchall()
                print("RESULT: ", result)

            if result is not None:
                sensors = []
                for row in result:  # Format and fill the resulting sensor list
                    sensors.append({
                        "label": row[0],
                        "description": row[1],
                        "type": row[2]
                    })

                return sensors
        else:
            # If not connected to the local database, attempt to reconnect and retry
            print(
                "get_sensors_from_configuration Error while executing select statement : database is not connected, retrying")
            connect_to_local_db()
            return get_sensors_from_configuration(id_config)

    except Exception as e:
        # Handle any exceptions that may occur during the query execution
        print(f"Error finding sensors related to the configuration: {e}")
        if (e.errno == 2013):
            connect_to_local_db()
            return get_sensors_from_configuration(id_config)

    # Return None if no sensors found or if an error occurred
    return None


# DONE
def get_error_id_from_label(label):
    """!
    Finds the error id corresponding to the given label

    @param label: The label of the error
    @return: The corresponding error_id if found, None if nothing was found or an error occurred
    """
    global local_db, local_cursor
    try:
        # Check if the local database connection is established
        if local_db is not None and local_db.is_connected():
            query = "SELECT id_error FROM error_message WHERE label = %s"

            with local_cursor_protection:
                local_cursor.execute(query, (label,))

                # Fetch the result
                result = local_cursor.fetchone()
            if result:
                return result[0]
        else:
            # If not connected to the local database, attempt to reconnect and retry
            print(
                "get_error_id_from_label Error while executing select statement : database is not connected, retrying")
            connect_to_local_db()
            return get_error_id_from_label(label)

    except Exception as e:
        # Handle any exceptions that may occur during the query execution
        print(f"Error finding sensor type from id_type: {e}")
        if (e.errno == 2013):
            connect_to_local_db()
            return get_error_id_from_label(label)

    # Return None if the sensor type is not found or there are errors
    return None


# DONE
def get_user_from_login_and_password(login, password):
    """!
    Finds the user based on the provided login and password in the local database.

    @param login: The user's login.
    @param password: The user's password in non encrypted form.
    @return: The user details if found, otherwise None.
    """
    global local_db, local_cursor
    try:
        # Check if the local database connection is established
        if local_db is not None and local_db.is_connected():
            encrypted_password = encrypt_password(password)
            query = "SELECT * FROM user WHERE login = %s AND password = %s"

            with local_cursor_protection:
                local_cursor.execute(query, (login, encrypted_password))

                # Fetch the result
                result = local_cursor.fetchone()

                return result if result is not None else None

        else:
            print(
                "get_user_from_login_and_password Error while executing select statement : database is not connected, retrying")
            connect_to_local_db()
            return get_user_from_login_and_password(login, password)

    except Exception as e:
        # Handle any exceptions that may occur during the query execution
        print(f"Error finding user by login and password: {e}")
        if (e.errno == 2013):
            connect_to_local_db()
            return get_user_from_login_and_password(login, password)


# DONE
def update_user_connexion_status(id_user, connexion_status):
    """!
    Sets the connexion status to either 1 (connected) or 0 (disconnected) in the local db

    @param id_user: The user's id
    @param connexion_status: The connexion status wanted
    @return: 1 if successful, otherwise None
    """
    global local_db, local_cursor
    try:
        # Check if the local database connection is established
        if local_db is not None and local_db.is_connected():
            query = "UPDATE user SET connected = %s WHERE id_user = %s"

            with local_cursor_protection:
                local_cursor.execute(query, (connexion_status, id_user))

            return 1
        else:
            print("Error while executing update statement : database is not connected, retrying")
            connect_to_local_db()
            return update_user_connexion_status(id_user, connexion_status)

    except Exception as e:
        # Handle any exceptions that may occur during the query execution
        print(f"Error updating user connexion status: {e}")
        if (e.errno == 2013):
            connect_to_local_db()
            return update_user_connexion_status(id_user, connexion_status)

    # Return None if the user is not found or there are errors
    return None


# DONE
def get_new_config_id():
    """!
    Gives the config id to be used to create a new config for the current system by looking in the local database
    and finding the highest config number corresponding to the system, and adding 1

    @return the id to be used to create a new config for the current system
    """
    global local_db, local_cursor
    try:
        # Check if the local database connection is established
        if local_db is not None and local_db.is_connected():
            query = ("SELECT MAX(CAST(SUBSTRING(id_config, LOCATE('_', id_config) + 1, "
                     "(LENGTH(id_config) - LOCATE('_', id_config))) AS SIGNED)) "
                     "FROM configuration "
                     "WHERE SUBSTRING(id_config, 1, LOCATE('_', id_config) - 1) = 'syst%s';")

            system_id = get_system_id()

            with local_cursor_protection:
                local_cursor.execute(query, (system_id,))

                # Fetch the result
                result = local_cursor.fetchone()

            if result[0]:
                return add_system_id(
                    int(result[0]) + 1)  # Increment so that the next session created has the next id value
            else:
                return add_system_id(1)

        else:
            # If not connected to the local database, attempt to reconnect and retry
            print(
                "get_new_config_id Error while executing select statement : database is not connected, retrying")
            connect_to_local_db()
            return get_new_config_id()

    except Exception as e:
        # Handle any exceptions that may occur during the query execution
        print(f"Error getting system id: {e}")
        if (e.errno == 2013):
            connect_to_local_db()
            return get_new_config_id()


# DONE
def get_new_id_session(participant, id_config):
    """!
    @brief This functions returns the id of the last session created in the database + 1
    @param self : the instance
    @return the id of the last session created in the database
    """
    global local_db, local_cursor
    try:
        if local_db is not None and local_db.is_connected():

            query = "SELECT MAX(id_session) FROM observation WHERE participant=%s AND id_config=%s"
            values = (participant, id_config)
            with local_cursor_protection:
                local_cursor.execute(query, values)
                result = local_cursor.fetchone()

            return result[0] + 1 if result[0] else 1
        else:
            # If not connected to the local database, attempt to reconnect and retry
            print(
                "get_new_id_session Error while executing select statement : database is not connected, retrying")
            connect_to_local_db()
            return get_new_id_session(participant, id_config)
    except Exception as e:
        # Handle any exceptions that may occur during the query execution
        print(f"Error getting system id: {e}")
        if (e.errno == 2013):
            connect_to_local_db()
            return get_new_id_session(participant, id_config)


# DONE
def get_config_labels_ids(id_config=None):
    """!
    Gets the labels and ids of either all configs in the local database if id_config is none, or the label of a specific
    config if id_config is not None and id_config too

    @param id_config: The config's id, if left at None, the function will get all config labels in the local database
    @return: One or more configuration labels if successful, None otherwise
    """
    global local_db, local_cursor
    try:
        # Check if the local database connection is established
        if local_db is not None and local_db.is_connected():
            if id_config is None:  # Grab all labels
                query = "SELECT id_config, label FROM configuration"

                with local_cursor_protection:
                    local_cursor.execute(query)
                    # Fetch the result
                    result = local_cursor.fetchall()

                if result:
                    return [{"id_config": row[0], "label": row[1]} for row in result]
                else:
                    return None

            else:  # Grab label associated with specific id
                query = "SELECT label FROM configuration WHERE id_config = %s"

                with local_cursor_protection:
                    local_cursor.execute(query, (id_config,))
                    result = local_cursor.fetchone()

                return result

        else:
            # If not connected to the local database, attempt to reconnect and retry
            print("Error while executing select statement: database is not connected, retrying")
            connect_to_local_db()
            return get_config_labels_ids(id_config)

    except Exception as e:
        # Handle any exceptions that may occur during the query execution
        print(f"Error getting config labels: {e}")
        if (e.errno == 2013):
            connect_to_local_db()
            return get_config_labels_ids(id_config)


# DONE
def create_observation(participant, id_config, id_session, session_label, active=0, id_system=None):
    """!
    Creates a new observation from the given parameters and inserts it in both databases

    @param id_system: The system's id
    @param participant: The participant's id
    @param id_config: The config's id
    @param id_session: The session's id
    @param session_label: The session's label
    @param active: The status of the session 1=active, 0=inactive
    @return None
    """
    if id_system is None:
        id_system = get_system_id()

    values = (id_system, participant, id_config, id_session, session_label, active)
    send_query('insert', 'observation',
               ['id_system', 'participant', 'id_config', 'id_session', 'session_label', 'active'],
               values)
    return None


# DONE
def create_configuration(id_config, id_user, label, description):
    """!
    Creates a new configuration from the given parameters and inserts it in both databases

    @param id_config: The config's id
    @param id_user: The id of the user who created the configuration
    @param label: The label of the configuration
    @param description: The description of the configuration
    @return None
    """

    values = (id_config, id_user, label, description)
    return send_query('insert', 'configuration', ['id_config', 'id_user', 'label', 'description'],
                      values)


# DONE
def create_sensor_configs(id_config, sensor_list):
    """!
    Creates the sensor configs in the databases for all the sensors in the given list

    @param id_config: The config id
    @param sensor_list: The list of sensors
    @return True if successful, False if one or more errors occurred
    """

    no_errors_encountered = True  # Used to know if any errors occurred in the loop

    for sensor_type_id, label, description in sensor_list:  # Go through the sensor list
        values = (id_config, sensor_type_id, label, description)
        # Send each query and check for errors
        result = send_query('insert', 'sensor_config',
                            ['id_config', 'id_sensor_type', 'sensor_label', 'sensor_description'],
                            values)
        if result == 0:  # No data stored in local nor remote
            no_errors_encountered = False

    return no_errors_encountered


def create_sensors(id_observation, sensor_list):
    """!
    Saves the information of one or more sensors in both databases

    @param id_observation: The observation id
    @param sensor_list: The list of sensors
    @return True if successful, False if one or more errors occurred
    """

    no_errors_encountered = True  # Used to know if any errors occurred in the loop

    if id_observation is None:
        return False

    types_list = get_sensor_type_list()

    for sensor in sensor_list:  # Go through the sensor list
        id_type = None
        for id, type in types_list:  # Get the corresponding id_type
            if sensor["type"] == type:
                id_type = id
                break

        if id_type is None:
            print("Sensor type not found in types list")
            return False

        values = (sensor["ieee_address"], id_type, id_observation, sensor["label"], sensor["description"])

        # Check for any errors while sending data
        result = send_query('insert', 'sensor',
                            ['MAC_address_sensor', 'id_type', 'id_observation', 'label', 'description'],
                            values)
        if result == 0:  # No data stored in local nor remote
            no_errors_encountered = False

    return no_errors_encountered


# DONE
def encrypt_password(password):
    """!
    Encrypts the given password using SHA-256

    @param password: The unencrypted password
    @return: The encrypted password
    """
    return hashlib.sha256(password.encode()).hexdigest()


# DONE
def get_active_observation():
    """!
    Select and return the ID of the active observation.

    @return A list of ID of active observations. Empty list if no active observations are found.
    """

    query = "SELECT id_observation FROM observation WHERE active = 1;"
    global local_db, local_cursor
    try:
        if local_db is not None and local_db.is_connected():
            with local_cursor_protection:
                local_cursor.execute(query)
                rows = local_cursor.fetchall()
            if rows:
                return rows[0]
            else:
                return None
        else:
            # If not connected to the local database, attempt to reconnect and retry
            print("get_active_observation Error while executing select statement : database is not connected, retrying")
            connect_to_local_db()
            return get_active_observation()
    except Exception as e:
        # Handle any exceptions that may occur during the query execution
        print(f"Error finding active observation : {e}")
        if (e.errno == 2013):
            connect_to_local_db()
            return get_active_observation()


# DONE
def get_sensors_from_observation(id_observation):
    """!
    Retrieve all sensor labels and their associated types for a given observation ID.

    @param id_observation : The ID of the observation.

    @return A list of dictionaries with keys "type" and "label" for each sensor. None list if no sensors are found.
    """

    query = """
    SELECT s.label, st.type 
    FROM sensor s 
    JOIN sensor_type st ON s.id_type = st.id_type 
    WHERE s.id_observation = %s;
    """
    global local_db, local_cursor
    try:
        if local_db is not None and local_db.is_connected():
            with local_cursor_protection:
                local_cursor.execute(query, id_observation)
                rows = local_cursor.fetchall()
            if rows:
                return [{"label": row[0], "type": row[1]} for row in rows]
            else:
                return None
        else:
            # If not connected to the local database, attempt to reconnect and retry
            print(
                "get_sensors_from_observation Error while executing select statement : database is not connected, retrying")
            connect_to_local_db()
            return get_sensors_from_observation(id_observation)
    except Exception as e:
        # Handle any exceptions that may occur during the query execution
        print(f"Error finding sensors from observation : {e}")
        if e.errno == 2013:
            connect_to_local_db()
            return get_sensors_from_observation(id_observation)


def get_observation_info(id_observation, field=None):
    """
    Retrieves all available information given observation ID. If param field is set, returns only this field

    @param id_observation : The ID of the observation.
    @param field : the particular field requested (if none selected, all fields will be returned)

    @return A list of the fields and their values. None list if nothing was found or an error occurred.
    Returns only one value if field was set.
    """

    global local_db, local_cursor
    try:
        if local_db is not None and local_db.is_connected():
            if field is None:   # No particular fields wanted
                query = """SELECT * FROM observation o WHERE o.id_observation = %s;"""
                with local_cursor_protection:
                    local_cursor.execute(query, (id_observation,))
                    result = local_cursor.fetchone()
                if result:
                    return [{"id_observation": result[0],
                             "id_system": result[1],
                             "participant": result[2],
                             "id_config": result[3],
                             "id_session": result[4],
                             "session_label": result[5],
                             "active": result[6]}]
                else:
                    return None
            else:   # Select one particular field
                query = """SELECT %s FROM observation o WHERE o.id_observation = %s;"""
                with local_cursor_protection:
                    local_cursor.execute(query, (field, id_observation,))
                    result = local_cursor.fetchone()
                if result:
                    return result
                else:
                    return None
        else:
            # If not connected to the local database, attempt to reconnect and retry
            print(
                "get_observation_info Error while executing select statement : database is not connected, retrying")
            connect_to_local_db()
            return get_observation_info(id_observation)
    except Exception as e:
        # Handle any exceptions that may occur during the query execution
        print(f"Error finding observation info : {e}")
        if e.errno == 2013:
            connect_to_local_db()
            return get_observation_info(id_observation)


def config_label_exists(label):
    """!
     Checks if a config with this label already exists in the local database

     @param label: The label to look for
     @return: The number of labels in the database that are identical to the on provided
     """
    global local_db, local_cursor
    try:
        # Check if the local database connection is established
        if local_db is not None and local_db.is_connected():
            query = "SELECT COUNT(*) FROM configuration WHERE label = %s"

            with local_cursor_protection:
                local_cursor.execute(query, (label,))

                # Fetch the result
                result = local_cursor.fetchone()
            if result == 0:
                return result
            else:
                return 1
        else:
            # If not connected to the local database, attempt to reconnect and retry
            print("config_label_exists Error while executing select statement : database is not connected, retrying")
            connect_to_local_db()
            return config_label_exists(label)

    except Exception as e:
        # Handle any exceptions that may occur during the query execution
        print(f"Error checking conflicting labels: {e}")
        if (e.errno == 2013):
            connect_to_local_db()
            return config_label_exists(label)
    # Return None if the sensor type is not found or there are errors
    return None
