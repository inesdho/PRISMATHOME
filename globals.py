"""!
@file globals.py

@brief This file is used to define all the global variables that we need to use.

@author Naviis-Brain

@version 1.0

@date 28th Decembre 2023
"""

# TODO faire de la doc et des commentaires pour ce fichier

# Bit used to close the connections thread when the window is closed
global_disconnect_request = False
# Bit used to know if the observation is in only_local mode or not (0 : not only_local, 1: only_local)
global_observation_mode = 0

global_id_user = None
sensor_counts = {}
global_id_config = None
global_sensor_entries = []
global_scenario_name_configuration = None
global_description_configuration = None

global_id_config_selected = None
global_new_id_observation = None

global_participant_selected = None
global_session_label_selected = None
global_id_system_selected = None
global_id_session_selected = None

global_is_modification = False

# Bit used to close threads get_sensor_value
thread_done = False

global_id_config_modify= None

global_font_title = ("Arial", 18, "bold")
global_font_title1 = ("Calibi", 12, "bold")
global_font_text = ("Calibi", 10)
