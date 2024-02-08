"""!
@file globals.py

@brief This file is used to define all the global variables that we need to use.

@author Naviis-Brain

@version 1.0

@date 31st January 2024
"""

# Bit used to close the connections thread when the window is closed
global_disconnect_request = False
# Bit used to know if the observation is in only_local mode or not (0 : not only_local, 1: only_local)
global_observation_mode = 0

# ID of the user logging in as admin
global_id_user = None

# List of the number of sensors selected by type
sensor_counts = {}

# Contains information about each sensor (sensor_type_id, label, description, unique_id)
global_sensor_entries = []

# Contain the id, label and description of the configuration the admin is creating
global_id_config = None
global_scenario_name_configuration = None
global_description_configuration = None

# Id of the config selected in the drop-down menu to make a new observation
global_id_config_selected = None

# Participant and session label entered to make a new observation
global_participant_selected = None
global_session_label_selected = None

# Id of the system on which the observation is launched
global_id_system_selected = None

# Id corresponding to the number of sessions the participant has made on the selected config
global_id_session_selected = None

# Contains the id of the new observation in progress on the machine
global_new_id_observation = None


# Returns True if the admin modifies a config otherwise False
global_is_modification = False

# Bit used to close threads get_sensor_value
thread_done = False

# Contain the id, label and description of the configuration that the admin is modifying
global_id_config_modify = None
global_label_modify = None
global_description_modify = None

global_font_title = ("Arial", 18, "bold")
global_font_title1 = ("Calibi", 12, "bold")
global_font_text = ("Calibi", 10)