### New Relic Of Things - Build Script

## PREREQS
# Need to do these steps on laptop before putting card in Pi
# sudo dd if=<jessie_img_path>/2016-09-23-raspbian-jessie.img of=/dev/<microsd_card_device> bs=1m
# cat $NROT_CONFIG/config.txt >> <boot_drive_name>/config.txt
# cp NROT.zip <boot_drive_name>

# After logged in: 
# unzip $NROT_ZIP 
# /$NROT_CONFIG/bootstrapNROT.sh

## CONFIGS
NR_HOME=/home/pi/newrelic
NROT_HOME=$NR_HOME/NRoT
NROT_CONFIG=$NROT_HOME/config
NROT_LOGS=$NROT_HOME/logs
NROT_ZIP=$NR_HOME/NRoT.zip

## COMMANDS

# Lay down the files and directories
sudo mkdir -p /opt/newrelic
sudo chown pi:pi /opt/newrelic
sudo ln -s /opt/newrelic $NR_HOME
cd $NR_HOME
cd $NROT_HOME
mkdir $NROT_LOGS

# Set up the PI itself (networking, necessary packages)
sudo vi /etc/wpa_supplicant/wpa_supplicant.conf
sudo vi /etc/modprobe.d/8192cu.conf
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install npm

# Set up the 'app'
npm install
mv ./node_modules/node-insights/index.js ./node_modules/node-insights/index.js.bak
cp ./configs/index.js ./node_modules/node-insights
ln -s /sys/bus/w1/devices devices
grep -H "" devices/*/w1_slave > $NROT_HOME/logs/devices-test.out
sudo cp /opt/newrelic/NRoT/nrotCtrl.sh /etc/init.d/nrot
sudo update-rc.d nrot defaults

# Test the 'app'
sudo /etc/init.d/nrot start
sudo /etc/init.d/nrot status
cd $NROT_LOGS
cat nrot.out
cat nrot.err