"""!
@file system_function.py

@brief This file contains a collection of functions for managing system-level operations, including sending signals
to processes, retrieving process IDs, exporting queries to a file, and password encryption.

@author Naviis-Brain

@version 1.0

@date 28th December 2023
"""

import hashlib
import subprocess
import os
from model import local


def send_signal(pid, signal_number):
    """!
    @brief Send a signal "signal_name" to the script which has the "pid" specified.
    In order to have the correct permission the function call a compiled script which has the bit setuid.
    @param pid : The pid of the script we want to send the signal
    @param signal_number : The number of the signal we want to send
    @return None
    """
    script_path = "/home/share/PRISMATHOME/kill"
    subprocess.run([script_path, str(pid), str(signal_number)], check=True)


def get_pid_of_script(script_name):
    """!
    @brief Get the pid of the script "script_name"
    @param script_name The name of the script we want the pid of
    @return The pid of the script "script_name"
    """
    try:
        # 'ps' command execution to get the running processes
        process = subprocess.run(['ps', 'aux'], stdout=subprocess.PIPE, text=True)
        # Filtering the lines that contain the name of the script
        lines = process.stdout.split('\n')
        for line in lines:
            if script_name in line:
                parts = line.split()
                # The PID is generally the second output of 'ps aux'
                return int(parts[1])
    except Exception as e:
        print(f"Something wrong happened while looking for the script pid : {e}")
    return None


def export_remote_queries(file_path, remote_queries):
    """!
    Saves all the unsent remote queries in an SQL file
    @param file_path: The path of the file to save the queries into
    @param remote_queries: The list of remote queries
    @return True if the file was successfully created and filled, False otherwise
    """

    if not file_path:
        return False

    # Check if the file path exists and if not, check if the directory exists and create it if it doesn't
    if not os.path.exists(file_path):
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except OSError:
                print("Error while creating directory or file : ", OSError)
                return False

    # Open the file in write mode
    with open(file_path, 'w') as f:
        try:
            for query in remote_queries:
                query_as_string = str(query[1])
                f.write(query_as_string + ';\n')
        except Exception as e:
            print(f"Error while exporting queries :", e)
            return False
    local.delete_remote_queries(remote_queries)
    return True


def encrypt_password(password):
    """!
    Encrypts the given password using SHA-256

    @param password: The unencrypted password
    @return: The encrypted password
    """
    return hashlib.sha256(password.encode()).hexdigest()
