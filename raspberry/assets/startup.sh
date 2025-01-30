#!/bin/bash
cd home/turingmaschine/Desktop/
rm flask-app.tar
unzip flask-app-image.zip
sudo docker load < flask-app.tar

echo "open Webbrowser in Kiosk Mode"
chromium-browser --kiosk http://localhost:5000 &

# Start Container at Port 5000
sudo docker run --privileged -v /dev/gpiomem:/dev/gpiomem -v /sys:/sys -v /proc/device-tree:/proc/device-tree -p 5000:5000 flask-app:latest
