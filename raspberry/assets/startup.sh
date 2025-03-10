#!/bin/bash
cd home/turingmaschine/Desktop/
rm flask-app.tar
unzip flask-app-image.zip
sudo docker stop $(sudo docker ps -q)
sudo docker load < flask-app.tar

echo "open Webbrowser in Kiosk Mode"
chromium-browser --kiosk http://localhost:5000 &

# Start Container at Port 5000
sudo docker run --privileged --device /dev/gpiochip4 -v /dev/ttyACMO:/dev/ttyACMO -v /dev/gpiomem:/dev/gpiomem -v /sys:/sys -v /proc/device-tree:/proc/device-tree -p 5000:5000 flask-app:latest
lxterminal -e "bash -c 'sudo docker logs -f $(sudo docker ps -q -f ancestor=flask-app:latest); exec bash'" &
