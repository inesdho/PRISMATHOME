"""!
@file local.py

@brief This file is used communicate with the data base

@author Naviis-Brain

@version 1.0

@date 10th Decembre 2023
"""
import mysql.connector

# Connexion to the data base
db = None;

cursor = None;


def find_sensor_by_type_label(type, label):
    """!
    Select in the data base the active sensor matching type and label

    @param type : The sensor type.
    @param label : The sensor label.

    @return The ID of the sensor researched
    """
    query = """
    SELECT s.id_sensor 
    FROM Sensor s 
    JOIN Sensor_type st ON s.id_type = st.id_type 
    WHERE s.label = %s AND st.type = %s;
    """

    values = (label, type)

    try:
        cursor.execute(query, values)
        rows = cursor.fetchone()
        return rows[0]

    except mysql.connector.Error as error:
        print("Erreur lors de la recherche du capteur par type et nom:", error)
        return None


def save_datas(id, datas, datetime):
    """!
    Insert into the data base the datas collection by the coordinator from the sensor

    @param id : The ID of the sensor.
    @param datas : The datas sent by the sensor.
    @param datetime : The datetime when the datas had been received.

    @return None
    """
    query = """
        INSERT INTO `Data` (`timestamp`, `id_send_data_status`, `id_sensor`, `data`) 
        VALUES (%s, %s, %s, %s);
    """
    values = (datetime, 0, id, datas)
    try:
        cursor.execute(query, values)
        db.commit()
    except mysql.connector.Error as error:
        print("Error inserting the datas from sensor id : ")


def set_battery_low(id):
    print("test")
    # TODO : update the monitoring table


def save_sensor_battery(id, battery):
    """!
    Update the battery percentage of a sensor in the database

    @param id: The ID of the sensor.
    @param battery_percentage: The new battery percentage value.
    """
    query = """
    UPDATE Sensor
    SET battery_percentage = %s
    WHERE id_sensor = %s;
    """
    values = (battery, id)

    try:
        cursor.execute(query, values)
        db.commit()
        print("Battery percentage updated for sensor id : ", id)
    except mysql.connector.Error as error:
        print("Error updating battery percentage: ", error)

    if (battery < 10):
        print("Battery low")
        # set_battery_low(id)

# faire quelque chose d'utile avec la connexion
