import subprocess
import os


# TODO faire la doc
def send_signal(pid, signal_name):
    script_path = "/home/share/PRISMATHOME/test"
    subprocess.run([script_path, str(pid), str(signal_name)], check=True)


def get_pid_of_script(script_name):
    """!
    @brief Get the pid of the script "script_name"
    @param script_name The name of the script that we want to get the pid
    @return The pid of the script "script_name"
    """
    try:
        # Exécution de la commande 'ps' pour obtenir les processus en cours
        process = subprocess.run(['ps', 'aux'], stdout=subprocess.PIPE, text=True)
        # Filtrage des lignes qui contiennent le nom du script
        lines = process.stdout.split('\n')
        for line in lines:
            if script_name in line:
                parts = line.split()
                # Le PID est généralement le deuxième élément dans la sortie de 'ps aux'
                return int(parts[1])
    except Exception as e:
        print(f"Erreur lors de la recherche du PID: {e}")
    return None


def export_remote_queries(file_path, remote_queries):
    """!
    Saves all the unsent remote queries in an SQL file
    @param file_path: The path of the file to save the queries into
    @param remote_queries: The list of remote queries
    @return True if the file was successfully created and filled, False otherwise
    TODO finish and test this function
    """

    print("File path = ", file_path)
    print("Remote queries = ", remote_queries)

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
    return True
