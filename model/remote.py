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

import globals

# Connexion to the database
thread_active = 0  # is used to know if the program is actively trying to reconnect to the remote db
disconnect_request = 0  # is used to stop the connect thread from looping

flag_synchro = False

db_protection = False
pool = None

ids_to_modify = ['id_sensor', 'id_data', 'id_observation']
tables_to_prepend = ['sensor', 'data', 'observation']

config = {
    "host": "192.168.1.22",
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
        if globals.global_disconnect_request:
            return
        # Création d'un pool de connexions
        pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="mypool",
            pool_size=3,
            **config
        )
        thread_active = 0
        print("\033[96mConnected to remote database\033[0m")
        synchronise_queries()
    except Exception as e:
        time.sleep(1)
        # Loop until the connection works
        connect_to_remote_db()


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
        print("\033[91mErreur connexion à la bdd distante" "En executant : ", query, "values", values, "\033[0m")

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

    print("Synchronising data between local and remote databases")

    # Wait until caching is finished
    while local.caching:
        pass

    query = "SELECT * FROM remote_queries"
    queries = local.execute_query_with_reconnect(query)

    if not queries:
        print("\033[93msynchronise_queries : No queries\033[0m")
        return
    try:
        for query_entry in queries:
            query = query_entry[1]
            success = execute_remote_query(query, None, True)
            if success:
                # If the query was executed successfully, delete the entry from the local table
                # TODO faire le delete avec l'id (à rajouter dans la bdd)
                local.send_query_local('delete', 'remote_queries', None, None, f"query = \"{query}\"")
    except Exception as e:
        print("Error while synchronising : ", e)

    print("Synchro sortie normale")
