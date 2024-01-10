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

import local

# Connexion to the database
db = None
cursor = None
thread_active = 0  # is used to know if the program is actively trying to reconnect to the remote db
disconnect_request = 0  # is used to stop the connect thread from looping

ids_to_modify = ['id_sensor', 'id_system', 'id_data', 'id_observation']

def connect_to_remote_db():
    """!
    Tries to connect to the remote database at an interval of 2 seconds. This function is used by other functions in
    an asynchronous manner using a thread, so it doesn't block the main program
    """
    global db, cursor, thread_active, disconnect_request

    thread_active = 1
    disconnect_request = 0
    while not disconnect_request:
        try:
            db = mysql.connector.connect(
                host="192.168.1.122",
                user="prisme",
                password="Q3fhllj2",
                database="prisme@home_ICM"
            )
            cursor = db.cursor()
            synchronise_queries()
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
            print("failed to disconnect from distant db")
            print(e)
    else:
        print("already disconnected from distant db")


def execute_remote_query(query, values=None):
    """!
    Tries to insert into the remote database the query and values passed as arguments
    @param query the query to be inserted
    @param values the values of said query
    @return 1 if successfully inserted, 0 otherwise
    """
    global db, cursor

    if db is not None and db.is_connected():  # checks if connected to the remote DB
        try:
            if values is not None:
                cursor.execute(query, values)
            else:
                cursor.execute(query)
            db.commit()  # No errors, query inserted in the remote db
            return 1
        except mysql.connector.Error as error:
            # Error inserting the data in distant base
            print(error)
            return 0
    else:
        print("Distant database not connected")
        # Create thread to check on the database
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
            # Fetch all entries from the 'remote_queries' table
            local.local_cursor.execute("SELECT * FROM remote_queries")
            queries = local.local_cursor.fetchall()
            for query_entry in queries:
                print("Query: ", query_entry[1])
                query = query_entry[1]
                success = execute_remote_query(query)
                if success:
                    # If the query was executed successfully, delete the entry from the local table
                    local.local_cursor.execute("DELETE FROM remote_queries WHERE query = %s", (query,))
                    local.local_db.commit()
        except Exception as e:
            print(f"Error syncing failed queries: {e}")
        else:
            print("Distant database not connected")
            # Create thread to check on the database
            if thread_active == 0:
                connection_thread = threading.Thread(target=connect_to_remote_db)
                connection_thread.start()
            return 0

