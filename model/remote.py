"""!
@file remote.py

@brief This file is used communicate with the distant database

@author Naviis-Brain - Matteo

@version 1.0

@date 28th December 2023
"""
import threading
import time

import mysql.connector

from model import local

# Connexion to the database
thread_active = 0  # is used to know if the program is actively trying to reconnect to the remote db
disconnect_request = 0  # is used to stop the connect thread from looping

flag_synchro = False

db_protection = False
pool = None

ids_to_modify = ['id_sensor', 'id_data', 'id_observation']
tables_to_prepend = ['sensor', 'data', 'observation']

config = {
    "host": "192.168.1.122",
    "user": "prisme",
    "password": "Q3fhllj2",
    "database": "prisme@home_ICM"
}


# DONE
def connect_to_remote_db():
    """!
    Tries to connect to the local database and loops until successfully connected

    @return None
    """
    print("try to connect to remote database")
    global pool, thread_active
    thread_active = 1
    try:
        if disconnect_request == 1:
            return
        # Création d'un pool de connexions
        pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="mypool",
            pool_size=3,
            **config
        )
        thread_active = 0
        synchronise_queries()
        print("\033[96mConnected to remote database\033[0m")
    except Exception as e:
        time.sleep(1)
        # Loop until the connection works
        #connect_to_remote_db()


def disconnect_from_remote_db():
    """!
        Disconnects from the remote database
        @return:
    """
    global disconnect_request, pool

    disconnect_request = 1

    # Disconnect from the database
    pool.closeall()


def execute_remote_query(query, values=None, synchronise=False):
    """!
    Tries to insert into the remote database the query and values passed as arguments
    @param query the query to be inserted
    @param values the values of said query
    @param synchronise: TODO
    @return 1 if successfully inserted, 0 otherwise
    """
    print("Enterring execute_remote_query")
    global flag_synchro, thread_active

    conn = None
    cursor = None

    # If the connexion thread is active, we indicate the calling function to cache the query
    if thread_active:
        local.caching = True
        return 0
    # If the function is not called by the synchronise thread wait until the synchronisation is done
    if not synchronise:
        while flag_synchro:
            pass

    try:
        conn = pool.get_connection()
        cursor = conn.cursor()

        if values is not None:
            print("\033[94mExecuted in remote : ", query, "values", values, "\033[0m")
            cursor.execute(query, values)
        else:
            print("\033[94mExecuted in remote : ", query, "\033[0m")
            cursor.execute(query)

        conn.commit()  # No errors, query inserted in the remote db
        return 1
    except (mysql.connector.errors.InterfaceError, mysql.connector.errors.OperationalError) as e:
        # Error inserting the data in distant base
        print("\033[91mErreur ", error, "En executant : ", query, "values", values, "\033[0m")

        # Create thread to check on the database
        local.caching = True
        if thread_active == 0:
            connection_thread = threading.Thread(target=connect_to_remote_db)
            connection_thread.start()
        return 0
    finally:
        if conn:
            # Close the connection
            cursor.close()
            conn.close()


def synchronise_queries():
    """!
    Synchronises data between local database and remote database :
    Grabs all non sent queries from the local database's 'remote_queries' table and sends them to the remote database
    """

    # Wait until caching is finished
    while local.caching:
        pass

    remote_queries_list = local.get_remote_queries()

    if not remote_queries_list:
        return

    for query_entry in remote_queries_list:
        try:
            id_query = query_entry[0]
            remote_query = query_entry[1]
            success = execute_remote_query(remote_query, None, True)
            if success:
                # If the query was executed successfully, delete the entry from the local table
                local.send_query_local('delete', 'remote_queries',
                                       None, None, f"id_query = {id_query}")
        except Exception as e:
            print("Sync error : ", e)


def fetch_remote_configs(get_users, get_configs):
    """!
    Imports configuration, sensor_config and user tables from the remote database to the local database

    @param get_configs: set to 1 to import all configurations and sensor configs, 0 to skip this import
    @param get_users: set to 1 to import all users, 0 to skip this import
    @return: 1 if successful, 0 otherwise
    """
    conn = None
    cursor = None
    try:
        conn = pool.get_connection()
        cursor = conn.cursor()

        if get_users == 1:
            remote_query = "SELECT id_user, login, password FROM user"
            cursor.execute(remote_query)
            remote_users = cursor.fetchall()
            local_users = local.get_users()

            if remote_users is not None:
                if local_users is not None:
                    for remote_user in remote_users:    # Compare remote and local user lists
                        if remote_user not in local_users:   # If the remote user is not found in the local list
                            # append to the insert list to add this user
                            print("id_user à insérer : ", remote_user[0])
                            insertion = local.execute_query_with_reconnect(
                                f"INSERT INTO user (id_user, login, password) "
                                f"VALUES ('{remote_user[0]}', '{remote_user[1]}', '{remote_user[2]}');"
                            )
                            if insertion is None:
                                return 0
                else:
                    print("local_users is none")
                    for remote_user in remote_users:    # Compare remote and local user lists
                        # append to the insert list to add this user
                        insertion = local.execute_query_with_reconnect(
                            f"INSERT INTO user (id_user, login, password) "
                            f"VALUES ('{remote_user[0]}', '{remote_user[1]}', '{remote_user[2]}');\n"
                        )
                        if insertion is None:
                            return 0
        if get_configs == 0:
            return 1
        elif get_configs == 1:
            remote_query = "SELECT id_config, id_user, label, description FROM configuration"
            cursor.execute(remote_query)
            remote_configs = cursor.fetchall()
            local_configs = local.get_configurations()

            print("local_configs:", local_configs)
            print("remote_configs:", remote_configs)

            if remote_configs is not None:
                if local_configs is not None:
                    for remote_c in remote_configs:    # Compare remote and local config lists
                        if remote_c not in local_configs:   # If the remote user is not found in the local list
                            insertion = local.execute_query_with_reconnect(
                                f"INSERT INTO configuration (id_config, id_user, label, description) "
                                f"VALUES ('{remote_c[0]}', '{remote_c[1]}', '{remote_c[2]}', '{remote_c[3]}');\n"
                                )
                            if insertion is None:
                                return 0
                else:
                    for remote_c in remote_configs:    # Compare remote and local config lists
                        insertion = local.execute_query_with_reconnect(
                            f"INSERT INTO configuration (id_config, id_user, label, description) "
                            f"VALUES ('{remote_c[0]}', '{remote_c[1]}', '{remote_c[2]}', '{remote_c[3]}');\n"
                            )
                        if insertion is None:
                            return 0


            remote_query = "SELECT id_config, id_sensor_type, sensor_label, sensor_description FROM sensor_config"
            cursor.execute(remote_query)
            remote_sensor_configs = cursor.fetchall()
            local_sensor_configs = local.get_sensor_configs()

            if remote_sensor_configs is not None:
                if local_sensor_configs is not None:
                    for remote_sc in remote_sensor_configs:  # Compare remote and local sensor config lists
                        if remote_sc not in local_sensor_configs:  # If the sensor config is not in the local db
                            insertion = local.execute_query_with_reconnect(
                                f"INSERT INTO sensor_config (id_config, id_sensor_type, sensor_label, sensor_description) "
                                f"VALUES ('{remote_sc[0]}', '{remote_sc[1]}', '{remote_sc[2]}', '{remote_sc[3]}');\n"
                            )
                            if insertion is None:
                                return 0
                else:
                    for remote_sc in remote_sensor_configs:  # Compare remote and local sensor config lists
                        insertion = local.execute_query_with_reconnect(
                            f"INSERT INTO sensor_config (id_config, id_sensor_type, sensor_label, sensor_description) "
                            f"VALUES ('{remote_sc[0]}', '{remote_sc[1]}', '{remote_sc[2]}', '{remote_sc[3]}');\n"
                        )
                        if insertion is None:
                            return 0
            return 1

        else:
            return 1
    except (mysql.connector.errors.InterfaceError, mysql.connector.errors.OperationalError) as e:
        # Error inserting the data in distant base
        print("\033[91mErreur :", e, "Dans la fonction de synchro distant vers local\033[0m")
        return 0

    finally:
        if conn:
            # Close the connection
            cursor.close()
            conn.close()
