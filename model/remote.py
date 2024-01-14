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
db = None
cursor = None
thread_active = 0  # is used to know if the program is actively trying to reconnect to the remote db
disconnect_request = 0  # is used to stop the connect thread from looping

flag_synchro = False

ids_to_modify = ['id_sensor', 'id_data', 'id_observation']
tables_to_prepend = ['sensor', 'data', 'observation']


def connect_to_remote_db():
    """!
    Tries to connect to the remote database at an interval of 2 seconds. This function is used by other functions in
    an asynchronous manner using a thread, so it doesn't block the main program
    """
    global db, cursor, thread_active, disconnect_request, flag_synchro

    thread_active = 1
    disconnect_request = 0
    while not disconnect_request:
        try:
            db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Q3fhllj2",
                database="prisme@home_ICM"
            )
            cursor = db.cursor()
            print("Connected to remote database")
            flag_synchro = True
            synchronise_queries()
            flag_synchro = False
            thread_active = 0
            break  # Break out of the loop if synchronization is successful

        except Exception as e:
            print("Failed to connect to remote DB. Retrying")
            print(e)
            time.sleep(2)

    else:
        print("Disconnect request")
        time.sleep(2)

def disconnect_from_remote_db():
    """!
        Disconnects from the remote database
        @return:
    """
    global db, cursor, disconnect_request
    if db is not None and db.is_connected():
        try:
            db = None
            cursor = None
            disconnect_request = 1
            return 1

        except Exception as e:
            print("\033[91mfailed to disconnect from distant db\033[0m")
            print(e)
    else:
        print("already disconnected from distant db")


def execute_remote_query(query, values=None, synchronise=False):
    """!
    Tries to insert into the remote database the query and values passed as arguments
    @param query the query to be inserted
    @param values the values of said query
    @param synchronise: TODO
    @return 1 if successfully inserted, 0 otherwise
    """
    global db, cursor, flag_synchro, thread_active

    if (db is not None and db.is_connected()):  # checks if connected to the remote DB
        try:
            if not synchronise:
                while flag_synchro:
                    pass

            if values is not None:
                print("\033[94mExecuted in remote : ", query, "values", values, "\033[0m")
                cursor.execute(query, values)
            else:
                print("\033[94mExecuted in remote : ", query, "\033[0m")
                cursor.execute(query)

            db.commit()  # No errors, query inserted in the remote db
            return 1
        except mysql.connector.Error as error:
            # Error inserting the data in distant base
            print("\033[91mErreur ", error, "En executant : ", query, "values", values, "\033[0m")
            raise
    else:
        print("\033[91mDistant database not connected req : ", query, "values", values, "\033[0m")

        # Create thread to check on the database
        local.caching = True
        if thread_active == 0:
            connection_thread = threading.Thread(target=connect_to_remote_db)
            connection_thread.start()
        return 0


def synchronise_queries():
    """!
    Synchronises data between local database and remote database :
    Grabs all non sent queries from the local database's 'remote_queries' table and sends them to the remote database
    """
    print("Synchronising data between local and remote databases")
    if db is not None and db.is_connected():
        try:
            print("local.caching = ", local.caching)
            while local.caching:
                print("Wait for the end of caching")
            print("Fin while local.caching")
            try:
                print("Entering 2nd try sychro")
                if local.local_db is not None and local.local_db.is_connected():
                    # Fetch all entries from the 'remote_queries' table
                    print("Waiting for local.cursor protection")
                    with local.local_cursor_protection:
                        print("Executing query SELECT * FROM remote_queries")
                        local.local_cursor.execute("SELECT * FROM remote_queries")
                        print("Selected")
                        queries = local.local_cursor.fetchall()
                        print("Fetched")
                        if queries is None:
                            print("\033[93msynchronise_queries : No queries\033[0m")
                            return
                else:
                    print("\033[93msynchronise_queries : PB DB\033[0m")
                    local.connect_to_local_db()
                    synchronise_queries()
                    return

            except Exception as e:
                print(f"\033[91mError select from remote_queries: {e}\033[0m")
                if e.errno == 2013:
                    connect_to_remote_db()
                    return
                print("Try to synchronise again")
                synchronise_queries()
                return

            for query_entry in queries:
                print("Syncro req : ", query_entry[1])
                query = query_entry[1]
                success = execute_remote_query(query,None,True)
                if success:
                    if local.local_db is not None and local.local_db.is_connected():
                        # If the query was executed successfully, delete the entry from the local table
                        with local.local_cursor_protection:
                            local.local_cursor.execute("DELETE FROM remote_queries WHERE query = %s", (query,))
                            local.local_db.commit()
        except Exception as e:
            print(f"\033[91mError syncing failed queries: {e}\033[0m")