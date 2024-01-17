import subprocess
import os
# TODO faire la doc
def send_sigterm(pid):
    script_path = "/home/prisme/Prisme@home/PRISMATHOME/kill_program.sh"
    subprocess.run(["sh", script_path, str(pid)], check=True)

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
    @return True if the file was successfully created and filled, 0 otherwise
    TODO
    """
