#!/bin/sh

# Setup the LEDs
echo 61 > /sys/class/gpio/export
echo out > /sys/class/gpio/gpio61/direction
echo 1 > /sys/class/gpio/gpio61/value

echo 44 > /sys/class/gpio/export
echo out > /sys/class/gpio/gpio44/direction
echo 1 > /sys/class/gpio/gpio44/value

echo 68 > /sys/class/gpio/export
echo out > /sys/class/gpio/gpio68/direction
echo 1 > /sys/class/gpio/gpio68/value

echo 67 > /sys/class/gpio/export
echo out > /sys/class/gpio/gpio67/direction
echo 1 > /sys/class/gpio/gpio67/value

# Setup the Buttons
echo 49 > /sys/class/gpio/export
echo in > /sys/class/gpio/gpio49/direction

echo 112 > /sys/class/gpio/export
echo in > /sys/class/gpio/gpio112/direction

echo 51 > /sys/class/gpio/export
echo in > /sys/class/gpio/gpio51/direction

echo 7 > /sys/class/gpio/export
echo in > /sys/class/gpio/gpio7/direction

echo 48 > /sys/class/gpio/export
echo in > /sys/class/gpio/gpio48/direction

ip link set can0 up type can bitrate 1000000

if [ -z "$STY" ]; then exec screen -dm -S eurobot /bin/bash "$0"; fi
while true; do
python3 /root/software/autostart/hauptsteuerung_main.py
done
