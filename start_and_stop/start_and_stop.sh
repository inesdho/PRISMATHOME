#! /bin/sh
    echo "Starting start_and_stop.py.py"

    # Init time with RTC
    echo ds1307 0x68 > /sys/class/i2c-adapter/i2c-1/new_device
    . /home/share/paho-mqtt/bin/activate
    python /home/share/PRISMATHOME/start_and_stop/start_and_stop.py

exit 0
