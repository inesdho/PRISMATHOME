"""!
@file local.py

@brief This file is used communicate with the local database

@author Naviis-Brain

@version 1.1

@date January 10 2024
"""

import globals

import mysql.connector
from mysql.connector import pooling
import time

from model.remote import send_query_remote

from system import system_function

# The local pool of connection
pool = None

# Flag to indicate if the caching function is running (True) or not (False)
caching = False

# The config for remote database
config = {
    "host": "localhost",
    "user": "root",
    "password": "Q3fhllj2",
    "database": "prisme_home_1"
}


###############################################
#   Database connection and query execution   #
###############################################

def connect_to_local_db(cpt=0):
    """!
    Tries to connect to the local database and loops until successfully connected
    or 15 seconds time out is reached

    @return 1 if connection was successful, 0 otherwise
    """
    global pool
    try:
        if globals.global_disconnect_request:
            return
        # Creation of a connection pool
        pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="mypool",
            pool_size=3,
            **config
        )
        return 1
    except Exception:
        if cpt < 15:
            time.sleep(1)
            # Loop until the connection works
            return connect_to_local_db(cpt=cpt+1)
        else:
            return 0


def execute_query_with_reconnect(query, values=None, cursor=None, max_attempts=3):
    """
    Execute an SQL query with the option to reconnect on connection loss in the local database.

    This function attempts to execute a provided SQL query up to a maximum number of attempts. If the connection is lost,
    it tries to reconnect and re-execute the query. The function handles SELECT, INSERT, DELETE, and UPDATE queries
    differently in terms of return values.

    @param query: The SQL query string to be executed.
    @param values: Optional. The values to be used in the SQL query.
    @param cursor: Optional. A cursor object to an existing database connection. If None, a new connection is obtained.
    @param max_attempts: Optional. The maximum number of attempts to execute the query in case of connection issues.

    @return: Depending on the type of query:
             - SELECT: Returns all fetched results.
             - INSERT: Returns the ID of the last inserted row.
             - DELETE/UPDATE: Returns the count of rows affected.
             Returns None if the query execution fails after all attempts.
    """
    # A flag to retry or not on connection lost
    # if a transaction is started to rollback changes
    retry = True
    conn = None
    query_type = None
    for attempt in range(max_attempts):
        try:
            # Use existing connection or obtain a new one from the pool
            if not cursor:
                conn = pool.get_connection()
                cursor = conn.cursor()
            else:
                retry = False

            cursor.execute(query, values)

            query_type = query.strip().upper().split(" ")[0]
            if query_type == "SELECT":
                # For SELECT, return all results
                return cursor.fetchall()
            elif query_type == "INSERT":
                # For INSERT, return the ID of the last inserted row
                return cursor.lastrowid
            elif query_type in ["DELETE", "UPDATE"]:
                # For DELETE and UPDATE, return the number of affected rows
                return cursor.rowcount

        except (mysql.connector.errors.InterfaceError, mysql.connector.errors.OperationalError) as e:
            if not retry:
                print(f"Connection lost, don't retry Error: {e}")
                return None
            conn = None  # Reset the connectio
            print(f"Connection lost, attempting to reconnect. Attempt {attempt + 1}/{max_attempts}. Error: {e}")

        finally:
            if retry:
                if conn:
                    if query_type != "SELECT":
                        conn.commit()
                    cursor.close()
                    conn.close()

    # If all attempts fail
    return None


def send_query(query_type, table, fields=None, values=None, condition=None):
    """
    Facilitates the insertion, update, or deletion of data in both local and remote databases.

    It first applies these operations to the local database and then attempts to replicate them in the remote
    database. The function is designed to handle the synchronization of data between the local and remote
    databases.

    @param query_type: The type of SQL query ('INSERT', 'UPDATE', 'DELETE', etc.).
    @param table: The name of the database table to be queried.
    @param fields: Optional. List of field names for the query. Required for INSERT and UPDATE queries.
    @param values: Optional. List of values corresponding to the fields. Required for INSERT and UPDATE queries.
    @param condition: Optional. The condition for UPDATE or DELETE queries.

    @return: An integer indicating the result of the operation:
             - 1 if data was successfully sent to both local and remote databases.
             - 2 if data was only sent to the local database.
             - 0 if no data was stored.
    """

    result = send_query_local(query_type, table, fields, values, condition)

    if result == -1:
        return 0

    if send_query_remote(query_type, table, fields, values, condition, result) == 0:
        return 2

    return 1


def send_query_local(query_type, table, fields=None, values=None, condition=None, cursor=None):
    """
    Constructs and executes an SQL query in the local database.

    This function supports INSERT, UPDATE, and DELETE statements. It builds the query based on the parameters provided
    and executes it using the `execute_query_with_reconnect` function. For INSERT queries on the 'observation' table,
    it updates a global variable with the new ID.

    @param query_type: Type of SQL query ('INSERT', 'UPDATE', 'DELETE').
    @param table: The database table to be queried.
    @param fields: Optional. The fields to be used in the SQL query, required for INSERT and UPDATE queries..
    @param values: Optional. The values to be used in the SQL query, required for INSERT and UPDATE queries.
    @param condition: Optional. The condition for UPDATE and DELETE queries.
    @param cursor: Optional. A cursor object to an existing database connection. If None, a new connection is obtained.

    @return: The result of the query execution. Returns -1 if the query execution fails.
    """
    valid_query_types = ["INSERT", "UPDATE", "DELETE"]
    query = ""

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

    # Storing data in local DB
    result = execute_query_with_reconnect(query, values, cursor, 3)

    # If query did not work
    if result is None:
        return -1

    if query_type.upper() == "INSERT" and table == 'observation':
        globals.global_new_id_observation = result

    return result


def cache_query(remote_query, remote_values):
    """!
    Caches the query that couldn't be sent to the remote database, in the local database as plain text

    @param remote_query: the query to store
    @param remote_values: the values of said query
    """
    global caching

    # Formatting the query to be saved as a string
    if remote_values is not None:
        remote_values = tuple(repr(value) for value in remote_values)  # transform each element into a representation
        remote_query_as_text = remote_query.format(*remote_values) % remote_values
    else:
        remote_query_as_text = remote_query

    send_query_local("insert", "remote_queries", ("query",), (remote_query_as_text,))

    caching = False


def get_remote_queries():
    """
    Retrieves all the unsent remote queries stored in the 'remote_queries' table to export them in an SQL file

    @return The list of unsent remote queries.
    """
    query = "SELECT id_query, query FROM remote_queries"
    remote_queries_list = execute_query_with_reconnect(query)

    if remote_queries_list:
        return remote_queries_list
    else:
        return None


def delete_remote_queries(queries_list=None):
    """!
    Deletes one or multiple queries from the remote_queries table
    @param queries_list: the list of queries to be deleted. If empty, deletes all queries in the table

    @return 1 if successful, result of send_query_local() if an error occurred
    """
    error = False
    try:
        # Establish a new database connection
        conn = pool.get_connection()
        function_cursor = conn.cursor()

        # Start a new transaction
        function_cursor.execute("START TRANSACTION;")

        # Iterate through each sensor in the sensor list
        for id_query, query in queries_list:  # Go through the sensor list
            # Insert sensor configuration into the local database and check for errors
            result = send_query_local('delete', 'remote_queries', condition=f'id_query="{id_query}"',
                                      cursor=function_cursor)
            if result == -1:  # No data stored in local nor remote
                raise Exception("Error while deleting remote_queries")

        # Commit the transaction after successful inserts
        conn.commit()

    except Exception as e:
        # Handle exceptions, rollback the transaction and set error flag
        if conn:
            conn.rollback()
            error = True
            print(f"An error occurred, the transaction will be cancelled : {e}")
    finally:
        # Close the connection
        if conn:
            function_cursor.close()
            conn.close()
        # Exit the function if there was an error
        if error:
            return


###############################################
#               Sensor Management             #
###############################################


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


def get_sensor_from_type_label(sensor_type, label):
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


def get_sensors_from_configuration(id_config):
    """!
    Gets all the sensors associated with the given configuration id in the local database and returns them as a list

    @param id_config: The configuration id
    @return: A list of sensors formatted as such [{"label": "Sensor1","description": "Description1","type": "Type1"},...
    """

    query = (
        "SELECT sc.sensor_label, sc.sensor_description, st.type "
        "FROM sensor_config sc, sensor_type st  "
        "WHERE sc.id_config = %s  "
        "AND sc.id_sensor_type = st.id_type")

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
        print("Error while getting sensors from configuration : ", e)

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

    if sensor_type is None:  # Grab for all types
        query = "SELECT label, description FROM sensor WHERE id_observation =%s"
        values = (id_observation,)
    else:   # Grab only for selected sensor type
        query = "SELECT label, description FROM sensor WHERE id_observation =%s AND id_type = %s"
        values = (id_observation, sensor_type)

    result = execute_query_with_reconnect(query, values)

    if result:
        return [{"label": row[0], "description": row[1]} for row in result]
    else:
        return None


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


###############################################
#             Monitoring Functions            #
###############################################


def get_message_id_from_label(label):
    """!
    Finds the monitoring message id corresponding to the given label

    @param label: The label of the monitoring message
    @return: The corresponding message_id if found, None if nothing was found or an error occurred
    """

    query = "SELECT id_message FROM monitoring_message WHERE label = %s"

    result = execute_query_with_reconnect(query, (label,))

    if result:
        return result[0][0]

    # Return None if the message id is not found or there are errors
    return None


def monitor_sensor_availability(sensor_id, datetime, availability):
    """!
    Insert the monitoring message "Sensor availability offline" or "Sensor availability online"

    @param sensor_id: The ID of the sensor.
    @param datetime : The datetime when the datas had been received.
    @param availability: The sensor's availability
    @return result of the send_query function (1 if data sent to local and remote DB, 2 if sent only to local DB,
    0 if no data was stored)
    """
    if availability == 0:
        values = (sensor_id, get_system_id(), datetime, get_message_id_from_label('Sensor availability offline'))
    elif availability == 1:
        values = (sensor_id, get_system_id(), datetime, get_message_id_from_label('Sensor availability online'))
    else:
        return 0

    return send_query('insert', 'monitoring',
                      ['id_sensor', 'id_system', 'timestamp', 'id_message'],
                      values)


def monitor_battery_low(sensor_id, datetime):
    """!
    Insert the monitoring message "Sensor battery low"

    @param sensor_id: The ID of the sensor.
    @param datetime : The datetime when the datas had been received.

    @return result of the send_query function (1 if data sent to local and remote DB, 2 if sent only to local DB,
    0 if no data was stored
    """
    values = (sensor_id, get_system_id(), datetime, get_message_id_from_label('Sensor battery low'))
    return send_query('insert', 'monitoring', ['id_sensor', 'id_system', 'timestamp', 'id_message'], values)


def monitor_system_start_stop(datetime, system_status):
    """!
    Inserts a monitoring message to indicate that the system is powering off or powering on

    @param datetime : The datetime when the data has been received.
    @param system_status: The status of the system, 1 for on and 0 for off.
    @return result of the send_query function (1 if data sent to local and remote DB, 2 if sent only to local DB,
    0 if no data was stored)
    """
    if system_status == 0:
        values = (get_system_id(), datetime, get_message_id_from_label('System shut down by participant'))
    elif system_status == 1:
        values = (get_system_id(), datetime, get_message_id_from_label('System started up by participant'))
    else:
        return 0

    return send_query('insert', 'monitoring', ['id_system', 'timestamp', 'id_message'], values)


def monitor_observation_start_stop(datetime, observation_status):
    """!
    Insert the monitoring message "Observation started" or "Observation stopped"

    @param datetime : The datetime when the data has been received.
    @param observation_status: The status of the observation, 1 for started and 0 for stopped.
    @return result of the send_query function (1 if data sent to local and remote DB, 2 if sent only to local DB,
    0 if no data was stored)
    """
    if observation_status == 0:
        values = (get_system_id(), datetime, get_message_id_from_label('Observation stopped'))
    elif observation_status == 1:
        values = (get_system_id(), datetime, get_message_id_from_label('Observation started'))
    else:
        return 0

    return send_query('insert', 'monitoring', ['id_system', 'timestamp', 'id_message'], values)


###############################################
#               User Management               #
###############################################


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

    encrypted_password = system_function.encrypt_password(password)
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

    result = send_query_local("UPDATE", "user", ("connected",), (connexion_status, id_user),
                              "id_user = %s")
    if result != -1:
        return 1

    # Return None if the user is not found or there are errors
    return None


###############################################
#             Config Management               #
###############################################


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


def get_configurations(active=None):
    """
    Retrieves all configurations in the local database matching the active parameter if set

    @param active: 1 to get active configs, 0 to get non-active configs, None to get all configs
    @return A list of the fields and their values. None list if nothing was found or an error occurred.
    """
    if active is not None:
        query = """SELECT id_config, id_user, label, description FROM configuration WHERE active = %s;"""
        result = execute_query_with_reconnect(query, (active,))
    else:
        query = """SELECT id_config, id_user, label, description FROM configuration;"""
        result = execute_query_with_reconnect(query)
    if result:
        return [(row[0], row[1], row[2], row[3]) for row in result]
    else:
        return None


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


def get_config_labels_description_ids(id_config):
    """!
    Gets the label and description of a specific config from the local database.

    @param id_config: The config's id.
    @return: Tuple of (label, description) if successful, None otherwise.
    """
    query = "SELECT label, description FROM configuration WHERE id_config = %s"

    result = execute_query_with_reconnect(query, (id_config,))

    if result:
        # Return both label and description
        return result[0][0], result[0][1]
    else:
        return None


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
        # Establish a new database connection
        conn = pool.get_connection()
        cursor = conn.cursor()

        # Start a new transaction
        cursor.execute("START TRANSACTION;")

        values = (id_config, id_user, label, description, '1')

        # Insert configuration into the local database and check for errors
        result = send_query_local('insert', 'configuration', ['id_config', 'id_user', 'label', 'description', 'active'],
                                  values,
                                  None, cursor)

        if result == -1:
            raise Exception("Error while inserting configuration")

        # Iterate through each sensor in the sensor list
        for sensor_type_id, sensor_label, sensor_description in sensor_list:  # Go through the sensor list

            values = (id_config, sensor_type_id, sensor_label, sensor_description)
            # Insert sensor configuration into the local database and check for errors
            result = send_query_local('insert', 'sensor_config',
                                      ['id_config', 'id_sensor_type', 'sensor_label', 'sensor_description'],
                                      values, None, cursor)
            if result == -1:  # No data stored in local nor remote
                raise Exception("Error while inserting sensor configuration")

        # Commit the transaction after successful inserts
        conn.commit()

    except Exception as e:
        # Handle exceptions, rollback the transaction and set error flag
        if conn:
            conn.rollback()
            error = True
            print(f"An error occurred, the transaction will be cancelled : {e}")
    finally:
        # Close the connection
        if conn:
            cursor.close()
            conn.close()
        # Exit the function if there was an error
        if error:
            return

    values = (id_config, id_user, label, description)

    # Insert configuration into remote database
    send_query_remote('insert', 'configuration', ['id_config', 'id_user', 'label', 'description'], values, None)

    # Insert each sensor configuration into the remote database
    for sensor_type_id, sensor_label, sensor_description in sensor_list:
        values = (id_config, sensor_type_id, sensor_label, sensor_description)

        send_query_remote('insert', 'sensor_config',
                          ['id_config', 'id_sensor_type', 'sensor_label', 'sensor_description'],
                          values)


def update_configuration_status(config_status, id_config):
    """!
    Sets the configuration status to either 1 (active) or 0 (inactive) in both databases

    @param config_status: The observation status wanted 1 for active and 0 for inactive
    @param id_config: The observation's id (optional, the id stored globally by the program will be used if
    this is not set)
    @return: the result of send_query
    """

    result = send_query_local("UPDATE", "configuration", ("active",), (config_status, id_config),
                              "id_config = %s")
    if result != -1:
        return 1

    # Return None if the user is not found or there are errors
    return None


###############################################
#           Observation Management            #
###############################################

def get_active_observation():
    """!
    Select and return the IDs of active observations.

    @return A list of ID of active observations. Empty list if no active observations are found.
    """

    query = "SELECT id_observation FROM observation WHERE active = 1;"

    result = execute_query_with_reconnect(query)

    if result:
        return result[0][0]
    else:
        return None


def get_observation_mode():
    """!
    Select and return the mode of the active observation.

    @return : (0 : not only_local, 1 : only_local)
    """

    query = "SELECT only_local FROM observation WHERE active = 1;"

    result = execute_query_with_reconnect(query)

    if result:
        return result[0][0]
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


def get_new_id_session(participant, id_config):
    """
    Calculates the ID for the next session based on existing sessions in the database.

    @param participant: The identifier of the participant.
    @param id_config: The configuration ID associated with the session.

    @return: The ID for the next session to be created. Returns 1 if no previous sessions are found.
    """

    query = "SELECT MAX(id_session) FROM observation WHERE participant=%s AND id_config=%s"
    values = (participant, id_config)

    result = execute_query_with_reconnect(query, values)

    if result:
        if result[0][0]:
            return int(result[0][0]) + 1  # Increment so that the next session created has the next id value
    return 1


def create_observation_with_sensors(user, participant, id_config, id_session, session_label, sensor_list, only_local=0,
                                    active=0, id_system=None):
    """!
    Creates a new observation with associated sensors from the given parameters and inserts them in both databases.
    @param user: The linux user connected when the function is called
    @param id_system: The system's id (if None, it will be retrieved)
    @param participant: The participant's id
    @param id_config: The config's id
    @param id_session: The session's id
    @param session_label: The session's label
    @param sensor_list: The list of sensors associated with the observation
    @param only_local: Indicate if the observation should only work in local mode (0 : not local only, 1 : local only)
    @param active: The status of the session (1=active, 0=inactive)
    @return True if successful, False if one or more errors occurred
    """
    conn = None
    cursor = None
    error = False
    id_observation = None
    types_list = []
    id_list = []  # To store IDs of local database insertions
    try:
        conn = pool.get_connection()
        conn.start_transaction()

        cursor = conn.cursor()

        # Creation of the observation
        if id_system is None:
            id_system = get_system_id()

        values = (id_system, user, participant, id_config, id_session, session_label, only_local, active)
        id_observation = send_query_local('insert', 'observation',
                                          ['id_system', 'creator', 'participant', 'id_config', 'id_session',
                                           'session_label', 'only_local', 'active'],
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
            print(f"An error occurred, the transaction will be cancelled : {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()
        if error:
            return False

    values = (id_system, user, participant, id_config, id_session, session_label, only_local, active)
    # Insertion in the remote database for observation
    send_query_remote('insert', 'observation', ['id_system', 'creator', 'participant', 'id_config',
                                                'id_session', 'session_label', 'only_local', 'active'], values,
                      None, id_list[0])

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


###############################################
#           System ID Management              #
###############################################

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


def add_system_id(local_id):
    """!
    Prepends the system's ID to any local ID provided in order to store them into the distant database

    @param local_id the local ID to which the system ID needs to be added
    @return the modified ID to be inserted into the distant database
    """
    system_id = get_system_id()
    concat_id = f"syst{system_id}_{local_id}"
    return concat_id
