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
from mysql.connector import pooling

local_db = None
local_cursor = None

pool = None

local_db_thread_distant = None
local_cursor_thread_distant = None

disconnect_request = 0  # is used to stop the connect thread from looping

local_cursor_protection = threading.Lock()

local_cursor_protect = False

caching = False

config = {
    #"host": "192.168.1.22",
    "host": "localhost",
    #"user": "prisme",
    "user": "root",
    "password": "Q3fhllj2",
    "database": "prisme_home_1"
}


# DONE
def connect_to_local_db():
    """!
    Tries to connect to the local database and loops until successfully connected

    @return None
    """
    print("try to connect to local database")
    global pool
    try:
        if disconnect_request == 1:
            return
        # Création d'un pool de connexions
        pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="mypool",
            pool_size=3,
            **config
        )
        print("\033[96mConnected to local database\033[0m")
    except Exception as e:
        time.sleep(1)
        # Loop until the connection works
        connect_to_local_db()


def disconnect_from_local_db():
    """!
    Tries to connect to the local database and loops until successfully connected

    @return None
    """
    global disconnect_request

    disconnect_request = 1

    # Disconnect from the database
    pool.closeall()


# DONE
def get_system_id():
    """!
    Gets the id of the current system from the local database

    @return the system's ID if successful, None otherwise
    """

    # Create query
    query = """SELECT s.id_system FROM `system` s"""

    result = execute_query_with_reconnect(query)

    if result:
        return result[0][0]

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


def execute_query_with_reconnect(query, values=None, cursor=None, max_attempts=3):
    # A flag to retry or not on connection lost
    # if a transaction is started to rollback changes
    retry = True
    conn = None
    for attempt in range(max_attempts):
        try:
            # Utiliser la connexion existante ou obtenir une nouvelle du pool
            if not cursor:
                conn = pool.get_connection()
                cursor = conn.cursor()
            else:
                retry = False

            cursor.execute(query, values)

            query_type = query.strip().upper().split(" ")[0]
            if query_type == "SELECT":
                # Pour SELECT, retourner tous les résultats
                return cursor.fetchall()
            elif query_type == "INSERT":
                # Pour INSERT, retourner l'ID de la dernière ligne insérée
                return cursor.lastrowid
            elif query_type in ["DELETE", "UPDATE"]:
                # Pour DELETE et UPDATE, retourner le nombre de lignes affectées
                return cursor.rowcount

        except (mysql.connector.errors.InterfaceError, mysql.connector.errors.OperationalError) as e:

            if not retry:
                print(f"Connection lost, don't retry Error: {e}")
                return None
            conn = None  # Réinitialiser la connexion
            print(f"Connection lost, attempting to reconnect. Attempt {attempt + 1}/{max_attempts}. Error: {e}")

        finally:
            if retry:
                if conn:
                    if query_type != "SELECT":
                        conn.commit()
                    cursor.close()
                    conn.close()

    # Si toutes les tentatives échouent
    return None


def send_query_local(query_type, table, fields=None, values=None, condition=None, cursor=None):
    valid_query_types = ["INSERT", "UPDATE", "DELETE"]
    query = ""

    # *****************************************************************************#
    # *************************** CREATION DE LA REQUETE **************************#
    # *****************************************************************************#
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
    # *****************************************************************************#
    # *************************** FIN CREATION REQUETE ****************************#
    # *****************************************************************************#

    print(f"\033[92mTry execute (local) : {query, values}\033[0m")

    # *****************************************************************************#
    # *************************** EXECUTION DE LA REQUETE *************************#
    # *****************************************************************************#

    # Storing data in local DB
    result = execute_query_with_reconnect(query, values, cursor, 3)

    # If query did not work
    if result is None:
        return -1

    print(f"\033[92mExecuted (local) : {query, values}\033[0m")

    if query_type.upper() == "INSERT" and table == 'observation':
        globals.global_new_id_observation = result

    return result


def send_query_remote(query_type, table, fields=None, values=None, condition=None, last_id=None):
    remote_values = None
    remote_query = None

    # *****************************************************************************#
    # *************************** CREATION DE LA REQUETE **************************#
    # *****************************************************************************#
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
    # *****************************************************************************#
    # *************************** FIN CREATION REQUETE ****************************#
    # *****************************************************************************#

    # Attempting to send to remote DB
    if remote.execute_remote_query(remote_query, remote_values) == 1:  # Success
        return 1
    else:
        cache_query(remote_query, remote_values)
        return 0


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

    result = send_query_local(query_type, table, fields, values, condition)

    if result == -1:
        return 0

    if send_query_remote(query_type, table, fields, values, condition, result) == 0:
        return 2

    return 1


# DONE
def cache_query(remote_query, remote_values):
    """!
    Caches the query that couldn't be sent to the remote database, in the local database as plain text
    @param remote_query: the query to store
    @param remote_values: the values of said query
    """
    print("Début caching : ", remote_query, remote_values)
    global caching

    # Formatting the query to be saved as a string
    if remote_values is not None:
        remote_values = tuple(repr(value) for value in remote_values)  # transform each element into a representation
        remote_query_as_text = remote_query.format(*remote_values) % remote_values
    else:
        remote_query_as_text = remote_query

    send_query_local("insert", "remote_queries", "query", remote_query_as_text)

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
def monitor_battery_low(sensor_id, datetime):
    """!
    Insert the monitoring message "Sensor battery low"

    @param sensor_id: The ID of the sensor.
    @param datetime : The datetime when the datas had been received.

    @return result of the send_query function (1 if data sent to local and remote DB, 2 if sent only to local DB,
    0 if no data was stored
    """
    values = (sensor_id, get_system_id(), datetime, get_error_id_from_label('Sensor battery low'))
    return send_query('insert', 'monitoring', ['id_sensor', 'id_system', 'timestamp', 'id_error'], values)


# TODO : faire fonction 2 en 1
def monitor_system_shut_down_by_participant(datetime):
    """!
    Insert the monitoring message "System shut down by participant"

    @param datetime : The datetime when the datas had been received.

    @return result of the send_query function (1 if data sent to local and remote DB, 2 if sent only to local DB,
    0 if no data was stored
    """

    values = (get_system_id(), datetime, get_error_id_from_label('System shut down by participant'))
    return send_query('insert', 'monitoring', ['id_system', 'timestamp', 'id_error'], values)


def monitor_system_started_up_by_participant(datetime):
    """!
    Insert the monitoring message "System started up by participant"

    @param datetime : The datetime when the datas had been received.

    @return result of the send_query function (1 if data sent to local and remote DB, 2 if sent only to local DB,
    0 if no data was stored
    """

    values = (get_system_id(), datetime, get_error_id_from_label('System started up by participant'))
    return send_query('insert', 'monitoring', ['id_system', 'timestamp', 'id_error'], values)


# TODO : faire fonction 2 en 1
def monitor_observation_started(datetime):
    """!
    Insert the monitoring message "Observation started"

    @param datetime : The datetime when the datas had been received.

    @return result of the send_query function (1 if data sent to local and remote DB, 2 if sent only to local DB,
    0 if no data was stored
    """

    values = (get_system_id(), datetime, get_error_id_from_label('Observation started'))
    return send_query('insert', 'monitoring', ['id_system', 'timestamp', 'id_error'], values)


def monitor_observation_stopped(datetime):
    """!
    Insert the monitoring message "Observation stopped"

    @param datetime : The datetime when the datas had been received.

    @return result of the send_query function (1 if data sent to local and remote DB, 2 if sent only to local DB,
    0 if no data was stored
    """

    values = (get_system_id(), datetime, get_error_id_from_label('Observation stopped'))
    return send_query('insert', 'monitoring', ['id_system', 'timestamp', 'id_error'], values)


# TODO : faire fonction 2 en 1
def monitor_availability_offline(sensor_id, datetime):
    """!
    Insert the monitoring message "Sensor availability offline"

    @param sensor_id: The ID of the sensor.
    @param datetime : The datetime when the datas had been received.

    @return result of the send_query function (1 if data sent to local and remote DB, 2 if sent only to local DB,
    0 if no data was stored
    """
    values = (sensor_id, get_system_id(), datetime, get_error_id_from_label('Sensor availability offline'))
    return send_query('insert', 'monitoring', ['id_sensor', 'id_system', 'timestamp', 'id_error'], values)


def monitor_availability_online(sensor_id, datetime):
    """!
    Insert the monitoring message "Sensor availability online"

    @param sensor_id: The ID of the sensor.
    @param datetime : The datetime when the datas had been received.

    @return result of the send_query function (1 if data sent to local and remote DB, 2 if sent only to local DB,
    0 if no data was stored
    """
    values = (sensor_id, get_system_id(), datetime, get_error_id_from_label('Sensor availability online'))
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
        if monitor_battery_low(sensor_id, datetime) == 0:
            return False

    return True


# DONE
def get_sensor_type_from_id_type(id_type):
    """!
    Finds the sensor type corresponding to the given id_type in the local database.

    @param id_type: The id_type of the sensor.
    @return: The corresponding sensor type if found, otherwise None.
    """
    query = "SELECT type FROM sensor_type WHERE id_type = %s"

    result = execute_query_with_reconnect(query, (id_type,))

    if result:
        return result[0][0]

    return None


# DONE
def get_sensor_type_list():
    """!
    Gets all the sensor types and ids in the local database

    @return: The corresponding sensor type if found, otherwise None.
    """

    query = "SELECT id_type, type FROM sensor_type"

    result = execute_query_with_reconnect(query)

    if result:
        return result

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
    """!
    Select in the database the active sensor matching type and label

    @param sensor_type : The sensor type.
    @param label : The sensor label.

    @return The ID of the corresponding sensor, False if no sensor was found or an error occurred
    """

    query = """
        SELECT s.id_sensor 
        FROM sensor s 
        JOIN sensor_type st ON s.id_type = st.id_type
        JOIN observation o ON s.id_observation = o.id_observation
        WHERE s.label = %s AND st.type = %s AND o.active = 1;
    """
    values = (label, sensor_type)

    result = execute_query_with_reconnect(query, values)

    if result:
        return result[0][0]
    else:
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

    query = (
        "SELECT sc.sensor_label, sc.sensor_description, st.type "
        "FROM sensor_config sc, sensor_type st  "
        "WHERE sc.id_config = %s  "
        "AND sc.id_sensor_type = st.id_type")

    print("get_sensors_from_configuration : id_config = " + str(id_config))

    result = execute_query_with_reconnect(query, (id_config,))

    try:
        if result is not None:
            sensors = []
            for row in result:  # Format and fill the resulting sensor list
                sensors.append({
                    "label": row[0],
                    "description": row[1],
                    "type": row[2]
                })
            return sensors
    except Exception as e:
        print("Erreur dans la conversion du résultat : ", e)

    # Return None if no sensors found or if an error occurred
    return None


def get_sensor_configs():
    """!
        Gets all sensor configs from the local database.

        @return: The sensor configs list if found, otherwise None.
        """

    query = "SELECT id_config, id_sensor_type, sensor_label, sensor_description FROM sensor_config"

    result = execute_query_with_reconnect(query)

    if result:
        return [(row[0], row[1], row[2], row[3]) for row in result]
    else:
        return None


def get_sensor_info_from_observation(id_observation, sensor_type=None):
    """!
    Gets the labels and descriptions of all sensors for a specific observation. A sensor type can be selected in
    order to only get results for this type of sensor

    @param id_observation: the observation's id
    @param sensor_type: (optional : the type of sensor to look for)
    @return: a list of labels and descriptions for each sensor corresponding to the criteria, None if no sensors
    found or an error occurred
    """

    if sensor_type is None:  # Grab all labels
        query = "SELECT label, description FROM sensor WHERE id_observation =%s"
        values = (id_observation,)
    else:
        query = "SELECT label, description FROM sensor WHERE id_observation =%s AND id_type = %s"
        values = (id_observation, sensor_type)

    result = execute_query_with_reconnect(query, values)

    if result:
        return [{"label": row[0], "description": row[1]} for row in result]
    else:
        return None


# DONE
def get_error_id_from_label(label):
    """!
    Finds the error id corresponding to the given label

    @param label: The label of the error
    @return: The corresponding error_id if found, None if nothing was found or an error occurred
    """

    query = "SELECT id_error FROM error_message WHERE label = %s"

    result = execute_query_with_reconnect(query, (label,))

    if result:
        return result[0][0]

    # Return None if the sensor type is not found or there are errors
    return None


def get_users():
    """!
        Gets all users from the local database.

        @return: The user list if found, otherwise None.
        """

    query = "SELECT id_user, login, password, connected FROM user"

    result = execute_query_with_reconnect(query)

    if result:
        return [(row[0], row[1], row[2]) for row in result]
    else:
        return None


# DONE
def get_user_from_login_and_password(login, password):
    """!
    Finds the user based on the provided login and password in the local database.

    @param login: The user's login.
    @param password: The user's password in non encrypted form.
    @return: The user details if found, otherwise None.
    """

    encrypted_password = encrypt_password(password)
    query = "SELECT * FROM user WHERE login = %s AND password = %s"

    result = execute_query_with_reconnect(query, (login, encrypted_password))
    if result is not None and len(result) > 0:
        return result[0]
    else:
        return None


# DONE
def update_user_connexion_status(id_user, connexion_status):
    """!
    Sets the connexion status to either 1 (connected) or 0 (disconnected) in the local db for the user.
    @param id_user: user's id
    @param connexion_status: The connexion status wanted
    @return: 1 if successful, otherwise None
    """

    query = "UPDATE user SET connected = %s WHERE login = %s AND password = %s"

    result = send_query_local("UPDATE", "user", ("connected",), (connexion_status, id_user),
                              "id_user = %s")
    if result != -1:
        return 1

    # Return None if the user is not found or there are errors
    return None


def update_observation_status(observation_status, id_observation=None):
    """!
    Sets the observation status to either 1 (active) or 0 (inactive) in both databases

    @param id_observation: The observation's id (optional, the id stored globally by the program will be used if
    this is not set)
    @param observation_status: The observation status wanted 1 for active and 0 for inactive
    @return: the result of send_query
    """
    if id_observation is None:
        id_observation = globals.global_new_id_observation
    values = (observation_status,)
    return send_query('update', 'observation',
                      ['active'],
                      values,
                      "id_observation=" + str(id_observation))
    # TODO : voir avec Paul s'il faut faire d'autres traitements pour stopper reception.py


# DONE
def get_new_config_id():
    """!
    Gives the config id to be used to create a new config for the current system by looking in the local database
    and finding the highest config number corresponding to the system, and adding 1

    @return the id to be used to create a new config for the current system
    """
    query = ("SELECT MAX(CAST(SUBSTRING(id_config, LOCATE('_', id_config) + 1, "
             "(LENGTH(id_config) - LOCATE('_', id_config))) AS SIGNED)) "
             "FROM configuration "
             "WHERE SUBSTRING(id_config, 1, LOCATE('_', id_config) - 1) = 'syst%s';")

    system_id = get_system_id()

    result = execute_query_with_reconnect(query, (system_id,))

    if result:
        if result[0][0]:
            return add_system_id(
                int(result[0][0]) + 1)  # Increment so that the next session created has the next id value
    return add_system_id(1)


# DONE
def get_new_id_session(participant, id_config):
    """!
    @brief This functions returns the id of the last session created in the database + 1
    @param self : the instance
    @return the id of the last session created in the database
    """

    query = "SELECT MAX(id_session) FROM observation WHERE participant=%s AND id_config=%s"
    values = (participant, id_config)

    result = execute_query_with_reconnect(query, values)

    if result:
        if result[0][0]:
            return int(result[0][0]) + 1  # Increment so that the next session created has the next id value
    return 1


# DONE
def get_config_labels_ids(id_config=None):
    """!
    Gets the labels and ids of either all configs in the local database if id_config is none, or the label of a specific
    config if id_config is not None and id_config too

    @param id_config: The config's id, if left at None, the function will get all config labels in the local database
    @return: One or more configuration labels if successful, None otherwise
    """

    if id_config is None:  # Grab all labels
        query = "SELECT id_config, label FROM configuration"

        result = execute_query_with_reconnect(query)

        if result:
            return [{"id_config": row[0], "label": row[1]} for row in result]
        else:
            return None

    else:  # Grab label associated with specific id
        query = "SELECT label FROM configuration WHERE id_config = %s"

        result = execute_query_with_reconnect(query, (id_config,))

        if result:
            return result[0][0]


def get_config_label_from_observation_id(id_observation):
    """!
    Gets the lconfig label from a configuration matching

    @param id_observation: The config's id, if left at None, the function will get all config labels in the local
    database
    @return: One or more configuration labels if successful, None otherwise
    """
    query = ("SELECT configuration.label FROM configuration, observation "
             "WHERE observation.id_config=configuration.id_config AND observation.id_observation=%s")

    result = execute_query_with_reconnect(query, (id_observation,))
    if result:
        return result[0][0]
    else:
        return None


# DONE
def create_observation_with_sensors(user, participant, id_config, id_session, session_label, sensor_list, active=0,
                                    id_system=None):
    """!
    Creates a new observation with associated sensors from the given parameters and inserts them in both databases.

    @param id_system: The system's id (if None, it will be retrieved)
    @param participant: The participant's id
    @param id_config: The config's id
    @param id_session: The session's id
    @param session_label: The session's label
    @param sensor_list: The list of sensors associated with the observation
    @param active: The status of the session (1=active, 0=inactive)
    @return True if successful, False if one or more errors occurred
    """
    conn = None
    cursor = None
    error = False
    types_list = []
    id_list = []  # To store IDs of local database insertions
    try:
        conn = pool.get_connection()
        conn.start_transaction()

        cursor = conn.cursor()

        # Creation of the observation
        if id_system is None:
            id_system = get_system_id()

        values = (id_system, user, participant, id_config, id_session, session_label, active)
        id_observation = send_query_local('insert', 'observation',
                                          ['id_system', 'creator', 'participant', 'id_config', 'id_session',
                                           'session_label',
                                           'active'],
                                          values, None, cursor)

        if id_observation == 0:
            raise Exception("Error while inserting observation")
        id_list.append(id_observation)

        # Creation of the sensors
        types_list = get_sensor_type_list()
        for sensor in sensor_list:
            id_type = None
            for id, type in types_list:
                if sensor["type"] == type:
                    id_type = id
                    break

            if id_type is None:
                raise Exception("Sensor type not found in types list")

            values = (sensor["ieee_address"], id_type, id_observation, sensor["label"], sensor["description"])
            result = send_query_local('insert', 'sensor',
                                      ['MAC_address_sensor', 'id_type', 'id_observation', 'label', 'description'],
                                      values, None, cursor)

            if result == 0:
                raise Exception("Error while inserting sensor")
            id_list.append(result)
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
            error = True
            print(f"Une erreur est survenue, la transaction a été annulée : {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()
        if error:
            return False

    values = (id_system, user, participant, id_config, id_session, session_label, active)
    # Insertion in the remote database for observation
    send_query_remote('insert', 'observation', ['id_system', 'creator', 'participant', 'id_config', 'id_session', 'session_label', 'active'], values, None, id_list[0])

    # Insertion in the remote database for sensors
    for i, sensor in enumerate(sensor_list, start=1):
        id_type = None
        for id, type in types_list:
            if sensor["type"] == type:
                id_type = id
                break

        values = (sensor["ieee_address"], id_type, id_observation, sensor["label"], sensor["description"])
        send_query_remote('insert', 'sensor',
                          ['MAC_address_sensor', 'id_type', 'id_observation', 'label', 'description'],
                          values, None, id_list[i])


# DONE
def create_configuration(id_config, id_user, label, description, sensor_list):
    """!
    Creates a new configuration from the given parameters and inserts it in both databases.
    Inserts also the sensor list into the database

    @param id_config: The config's id
    @param id_user: The id of the user who created the configuration
    @param label: The label of the configuration
    @param description: The description of the configuration
    @param sensor_list: The list of sensors associated with the configuration
    @return None
    """
    conn = None
    cursor = None
    error = False

    try:
        conn = pool.get_connection()

        cursor = conn.cursor()
        cursor.execute("START TRANSACTION;")

        values = (id_config, id_user, label, description)
        result = send_query_local('insert', 'configuration', ['id_config', 'id_user', 'label', 'description'], values,
                                  None, cursor)

        if result == -1:
            raise Exception("Error while inserting configuration")

        for sensor_type_id, sensor_label, sensor_description in sensor_list:  # Go through the sensor list

            values = (id_config, sensor_type_id, sensor_label, sensor_description)
            # Send each query and check for errors
            result = send_query_local('insert', 'sensor_config',
                                      ['id_config', 'id_sensor_type', 'sensor_label', 'sensor_description'],
                                      values, None, cursor)
            if result == -1:  # No data stored in local nor remote
                raise Exception("Error while inserting sensor configuration")

        conn.commit()

    except Exception as e:
        if conn:
            conn.rollback()
            error = True
            print(f"Une erreur est survenue, la transaction a été annulée : {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()
        if error:
            return

    values = (id_config, id_user, label, description)
    send_query_remote('insert', 'configuration', ['id_config', 'id_user', 'label', 'description'], values, None)

    for sensor_type_id, sensor_label, sensor_description in sensor_list:
        values = (id_config, sensor_type_id, sensor_label, sensor_description)

        send_query_remote('insert', 'sensor_config',
                          ['id_config', 'id_sensor_type', 'sensor_label', 'sensor_description'],
                          values)


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

    result = execute_query_with_reconnect(query)

    if result:
        return result[0][0]
    else:
        return None


# DONE
def get_sensors_from_observation(id_observation):
    """!
    Retrieve all sensor labels and their associated types for a given observation ID.

    @param id_observation : The ID of the observation.

    @return A list of dictionaries with keys "type" and "label" for each sensor. None list if no sensors are found.
    """

    query = """SELECT s.label, st.type FROM sensor s 
    JOIN sensor_type st ON s.id_type = st.id_type 
    WHERE s.id_observation = %s;
    """

    result = execute_query_with_reconnect(query, (id_observation,))

    if result:
        return [{"label": row[0], "type": row[1]} for row in result]
    else:
        return None


def get_observation_info(id_observation, field=None):
    """
    Retrieves all available information given observation ID. If param field is set, returns only this field

    @param id_observation : The ID of the observation.
    @param field : the particular field requested (if none selected, all fields will be returned)

    @return A list of the fields and their values. None list if nothing was found or an error occurred.
    Returns only one value if field was set.
    """
    if field is None:  # No particular fields wanted
        query = """SELECT * FROM observation o WHERE o.id_observation = %s;"""
        result = execute_query_with_reconnect(query, (id_observation,))
        if result:
            elements = result[0]
            return [{"id_observation": elements[0],
                     "id_system": elements[1],
                     "participant": elements[2],
                     "id_config": elements[3],
                     "id_session": elements[4],
                     "session_label": elements[5],
                     "active": elements[6]}]
        else:
            return None
    else:  # Select one particular field
        query = f"""SELECT {field} FROM observation o WHERE o.id_observation = %s;"""
        result = execute_query_with_reconnect(query, (id_observation,))
        if result:
            return result[0][0]
        else:
            return None


def get_configurations():
    """
    Retrieves all configurations in the local database

    @return A list of the fields and their values. None list if nothing was found or an error occurred.
    """
    query = """SELECT id_config, id_user, label, description FROM configuration;"""
    result = execute_query_with_reconnect(query)
    if result:
        return [(row[0], row[1], row[2], row[3]) for row in result]
    else:
        return None


def config_label_exists(label):
    """!
     Checks if a config with this label already exists in the local database

     @param label: The label to look for
     @return: True if it exists, False if not. Returns -1 if an error occurred
     """
    query = """SELECT COUNT(*) FROM configuration WHERE label = %s;"""

    result = execute_query_with_reconnect(query, (label,))

    if result[0][0] == 0:
        return False
    else:
        return True
