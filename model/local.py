"""!
@file local.py

@brief This file is used communicate with the database

@author Naviis-Brain

@version 1.0

@date 28th Decembre 2023
"""
import mysql.connector
import time

import model.remote

local_db = None
local_cursor = None

def connect_to_local_db():
    """!
    Create a connexion to the local DB

    @return None
    """
    try:
        global local_db, local_cursor
        # Connexion to the database
        local_db = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="Q3fhllj2",
            database="prisme_home_1"
        )
        local_cursor = local_db.cursor()
    except Exception as e:
        time.sleep(1)
        # Loop until the connection works
        connect_to_local_db()

def get_system_id():
    """!
    Gets the id of the current system from the local database
    @return the system's ID
    """
    # TODO : Ajouter try except comme dans les autres fonctions
    global local_db, local_cursor

    query = """
        SELECT s.id_system 
        FROM system s
        """
    local_cursor.execute(query)
    result = local_cursor.fetchone()

    if result:
        system_id = result[0]
        return system_id
    else:
        print("System not found")
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

def find_sensor_by_type_label(sensor_type, label):
    """!
    Select in the database the active sensor matching type and label

    @param sensor_type : The sensor type.
    @param label : The sensor label.

    @return The ID of the sensor researched. False if no sensors has been found
    """
    global local_db, local_cursor

    query = """
    SELECT s.id_sensor 
    FROM sensor s 
    JOIN sensor_type st ON s.id_type = st.id_type
    JOIN observation o ON s.id_observation = o.id_observation
    WHERE s.label = %s AND st.type = %s AND o.active = 1;
    """

    values = (label, sensor_type)

    try:
        local_cursor.execute(query, values)
        rows = local_cursor.fetchone()
        if rows[0] is not None:
            return rows[0]
        else:
            return False
    except mysql.connector.Error as error:
        # 2013 is the error code for connection lost
        if error.errno == 2013:
            # CBD : Monitoring "Lost local DB connection at [datetime]"
            # Wait until the connection is back
            connect_to_local_db()
            # CBD : Monitoring "local DB connection at [datetime]"
            # Loop to retry the query
            return find_sensor_by_type_label(sensor_type, label)
        else:
            return False

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

        left, right = map(str.strip, condition.split('='))
        # Check if the condition's id needs to be modified
        if left in remote.ids_to_modify:
            right = str(add_system_id(right))  # Modifying the id to look for to prepend the system's id
        modified_condition = f"{left} = '{right}'"
        remote_query = f"{query_type} `{table}` SET "
        remote_query += ', '.join([f"{field} = %s" for field in fields])
        remote_query += f" WHERE {modified_condition}"

    elif query_type.upper() == "DELETE":
        if condition is None:
            raise ValueError(f"Condition is required for {query_type} queries.")
        query = f"{query_type} FROM `{table}`"
        query += f" WHERE {condition}"

    print(f"Trying to execute this query in local DB: {query, values}")

    try:
        # Storing data in local DB
        local_cursor.execute(query, values)
        local_db.commit()
        print("Executed query in local DB")

        # Building remote query
        # Appending system id to specific ids before sending to remote DB storing function
        if fields is not None and values is not None:
            remote_values = [add_system_id(value) if field in remote.ids_to_modify
                             else value for field, value in zip(fields, values)]
        # Check if the condition's id needs to be modified
        if condition is not None:
            left, right = map(str.strip, condition.split('='))
            if left in remote.ids_to_modify:
                right = str(add_system_id(right))  # Modifying the id to look for to prepend the system's id
            modified_condition = f"{left} = '{right}'"

        if query_type.upper() == "INSERT" and table.upper() == 'DATA':     # Need to add the data id in the remote base
            fields = ['id_data'] + fields
            remote_values = [add_system_id(local_cursor.lastrowid)] + remote_values
            remote_query = f"{query_type} INTO `{table}`"
            remote_query += f" ({', '.join(fields)}) VALUES ({', '.join(['%s'] * len(remote_values))})"

        elif query_type.upper() == "UPDATE":
            remote_query = f"{query_type} `{table}` SET "
            remote_query += ', '.join([f"{field} = %s" for field in fields])
            remote_query += f" WHERE {modified_condition}"

        elif query_type.upper() == "DELETE":
            remote_query = f"{query_type} FROM `{table}`"
            remote_query += f" WHERE {modified_condition}"
        # Appending system id to specific ids before sending to remote DB storing function
        # remote_values = None
        # if values is not None:
        #     remote_values = [add_system_id(value) if field in remote.ids_to_modify
        #                      else value for field, value in zip(fields, values)]
        #
        # if table.upper() == 'DATA' and query_type.upper() == 'INSERT':     # Need to add the data id in the remote base
        #     fields = ['id_data'] + fields
        #     remote_values = [add_system_id(local_cursor.lastrowid)] + remote_values
        #     query = f"{query_type} INTO `{table}`"
        #     query += f" ({', '.join(fields)}) VALUES ({', '.join(['%s'] * len(remote_values))})"
        print(f"Trying to execute this query in distant DB: {remote_query, remote_values}")

        # Attempting to send to remote DB
        if remote.execute_remote_query(query, remote_values) == 1:  # Success
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
            print("Unexpected error while storing to local DB!!!")
            print("Error (local):", error)
            return 0

def cache_query(remote_query, remote_values):
    """!
    Caches the query that couldn't be sent to the remote database, in the local database as plain text
    @param remote_query: the query to store
    @param remote_values: the values of said query
    """
    print("Caching")
    global local_db, local_cursor
    remote_query_as_text = None
    # Store the remote query in the cache table as plain text
    caching_query = """INSERT INTO `remote_queries` (`query`) VALUES (%s)"""
    # Formatting the query to be saved as a string
    if remote_values is not None:
        remote_values = tuple(repr(value) for value in remote_values)  # transform each element into a representation
        remote_query_as_text = remote_query.format(*remote_values) % remote_values
        print("Values not none")
    else:
        remote_query_as_text = remote_query
        print("Values none //////////////")
    print("remote_query_as_text  = ", remote_query_as_text)
    local_cursor.execute(caching_query, (remote_query_as_text,))
    local_db.commit()

def save_data(sensor_id, data, timestamp):
    """!
        Inserts into the database the data from the sensor

        @param sensor_id : The ID of the sensor.
        @param data : The data sent by the sensor.
        @param timestamp : The datetime when the data was received

        @return None
        """
    values = [sensor_id, data, timestamp]
    send_query('insert', 'data', ['id_sensor', 'data', 'timestamp'], values)

def save_sensor_battery(sensor_id, battery, datetime):
    """!
    Update the battery percentage of a sensor in the database

    @param sensor_id: The ID of the sensor.
    @param battery: The new battery percentage value.
    @param datetime: The timestamp when the data had been received
    """
    # TODO : (Matteo) Ajouter la gestion pour la BDD distante dans cette fonction
    query = """
    UPDATE sensor
    SET battery_percentage = %s
    WHERE id_sensor = %s;
    """
    values = (battery, sensor_id)

    try:
        local_cursor.execute(query, values)
        local_db.commit()
    except mysql.connector.Error as error:
        if error.errno == 2013:
            # CBD : Monitoring "Lost local DB connection at [datetime]"
            connect_to_local_db()
            # CBD : Monitoring "local DB connection at [datetime]"
            return save_sensor_battery(sensor_id, battery, datetime)
        else:
            return False

    if battery < 10:
        # update monitoring table
        set_battery_low(sensor_id, datetime)

    return True

def get_active_observation():
    """!
    Select and return the ID of the active observation.

    @return A list of ID of active observations. Empty list if no active observations are found.
    """

    query = "SELECT id_observation FROM observation WHERE active = 1;"

    try:
        local_cursor.execute(query)
        rows = local_cursor.fetchall()
        if rows:
            return rows[0]
        else:
            return None
    except mysql.connector.Error as error:
        # 2013 is the error code for connection lost
        if error.errno == 2013:
            # CBD : Monitoring "Lost local DB connection at [datetime]"
            # Wait until the connection is back
            connect_to_local_db()
            # CBD : Monitoring "local DB connection at [datetime]"
            # Loop to retry the query
            return find_active_observation()
        else:
            return False

def get_sensors_from_observation(id_observation):
    """
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

    try:
        local_cursor.execute(query, id_observation)
        rows = local_cursor.fetchall()
        if rows:
            return [{"label": row[0], "type": row[1]} for row in rows]
        else:
            return None
    except mysql.connector.Error as error:
        # 2013 is the error code for connection lost
        if error.errno == 2013:
            # CBD : Monitoring "Lost local DB connection at [datetime]"
            # Wait until the connection is back
            connect_to_local_db()
            # CBD : Monitoring "local DB connection at [datetime]"
            # Loop to retry the query
            return get_sensors_from_observation(id_observation)
        else:
            return False

"""********* Monitoring functions **********"""
def set_battery_low(sensor_id, datetime):
    """!
    Insert the monitoring message "Sensor battery low"

    @param sensor_id: The ID of the sensor.
    @param datetime : The datetime when the datas had been received.
    """
    # TODO : (Matteo) Ajouter la gestion pour la BDD distante dans cette fonction
    query = """
        INSERT INTO monitoring (id_sensor, id_system, timestamp, id_error)
        VALUES (%s, %s, %s, (SELECT id_error FROM Error_message WHERE label = 'Sensor battery low'));
        """
    data = (sensor_id, get_system_id(), datetime)
    try:
        local_cursor.execute(query, data)
        local_db.commit()
        return True
    except mysql.connector.Error as error:
        if error.errno == 2013:
            # CBD : Monitoring "Lost local DB connection at [datetime]"
            connect_to_local_db()
            # CBD : Monitoring "local DB connection at [datetime]"
            return set_battery_low(sensor_id, datetime)
        else:
            return False




