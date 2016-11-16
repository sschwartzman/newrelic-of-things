#!/bin/sh
cd /home/pi/New-Relic-of-Things
npm install
cat /home/pi/New-Relic-of-Things/config/config.txt >> /boot/config.txt
mv /etc/wpa_supplicant/wpa_supplicant.conf /boot
ln -s /boot/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf
