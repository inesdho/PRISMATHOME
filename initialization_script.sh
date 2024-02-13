#!/bin/bash

# Execute this script with sudo ./initialization_script.sh

# Create the ICM group
groupadd ICM

# Create the /home/share_test directory
mkdir /home/share

# Install the mosquitto broker for mqtt
sudo apt install mosquitto
# Install the virtualenv command
sudo apt install virtualenv


# Create a virtual environment named paho-mqtt inside /home/share_test
virtualenv /home/share/paho-mqtt
# Activate the virtual environment
source /home/share/paho-mqtt/bin/activate

# Install the library needed for the project
pip install paho-mqtt==1.6.1
pip install ttkthemes
pip install mysql-connector
pip install RPi.GPIO

# Copy paho.mqtt.python folder in the program folder
cp -r ./ /home/share

# Install paho-mqtt from the copied folder
cd /home/share/paho.mqtt.python
python setup.py install

# Give ownership of the /home/share directory to the root user and the ICM group
chown -R root:ICM /home/share
# Set permissions recursively for the /home/share directory to 770 (rwxr-xr-x)
chmod -R 770 /home/share
# Grant the sticky bit (setuid) to the file /home/share/PRISMEATHOME/kill
chmod u+s /home/share/PRISMEATHOME/kill

##############################################
############ INSTALL ZIGBEE2MQTT #############
##############################################

# Download the installation script for Node.js (version 16.x)
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -

# Install Node.js and other dependencies for ZIGBEE2MQTT
apt-get install -y nodejs git make g++ gcc #The node version use is V18.13.0
apt install npm #The npm version use is 9.2.0

# Create the /opt/zigbee2mqtt directory
mkdir /opt/zigbee2mqtt
# Change ownership of the /opt/zigbee2mqtt directory to the current user
chown -R ${USER}: /opt/zigbee2mqtt
# Clone the ZIGBEE2MQTT repository from GitHub
cp -r /home/share/zigbee2mqtt /opt/zigbee2mqtt
# Change directory to the ZIGBEE2MQTT installation directory
cd /opt/zigbee2mqtt
# Install the required npm packages
npm ci
# Build the ZIGBEE2MQTT project
npm run build
# Copy the configuration example file to the configuration file
cp /opt/zigbee2mqtt/data/configuration.example.yaml /opt/zigbee2mqtt/data/configuration.yaml
# Copy the systemd service file for ZIGBEE2MQTT
cp /home/share/zigbee2mqtt.service /etc/systemd/system

# Daemon-reload to update systemd service manager
systemctl daemon-reload
# Start the ZIGBEE2MQTT service
systemctl start zigbee2mqtt
# Enable the ZIGBEE2MQTT service to start automatically at boot
systemctl enable zigbee2mqtt.service

#######################################################
############ INSTALL MySQL and phpMyadmin #############
#######################################################

apt-get install apache2 php mariadb-server php-mysql
apt-get install phpmyadmin
# Restart Apache to apply the changes
sudo service apache2 restart

rootpasswd=""

# Grant all privileges to phpmyadmin user
#mysql -u root -p"$rootpasswd" -e "USE mysql; GRANT ALL PRIVILEGES ON *.* TO 'phpmyadmin'@'localhost'; FLUSH PRIVILEGES;"
echo "USE mysql; GRANT ALL PRIVILEGES ON *.* TO 'phpmyadmin'@'localhost'; FLUSH PRIVILEGES;" | mysql -u root -p"$rootpasswd"
# Define the start_and_stop program in the crontab to start it automatically on boot
#(crontab -l 2>/dev/null; echo "@reboot sh /home/share/PRISMEATHOME/start_and_stop/start_and_stop.sh > /home/share/log/log.txt 2>&1") | crontab -

# Disable the autologin
sed -i 's/^autologin-user=/#autologin-user=/g' /etc/lightdm/lightdm.conf

# set keyboard in azerty mode
sed -i 's/XKBLAYOUT=".*"/XKBLAYOUT="fr"/g' /etc/default/keyboard
