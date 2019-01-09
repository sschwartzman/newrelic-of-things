import sys
import json
import time
import urllib
import urllib3
from w1thermsensor import W1ThermSensor

# Required to set these
insights_account = "enter_your_account_id_here"
insights_license_key = "enter_your_insert_key_here"
sensor_location = "enter_sensor_location_here"

# Likely don't have to change these, but go for it if you want
debug = False
checkDelay = 30

# Don't mess with these
nroutput = {}
insights_url = "https://insights-collector.newrelic.com/v1/accounts/" + insights_account + "/events"
reserved_words = ['accountId','appId','duration','timestamp','type','YESTERDAY']
sensor = W1ThermSensor()
http = urllib3.PoolManager()

def add_to_insights():
    try:
        encoded_data = json.dumps(nroutput).encode('utf-8')
        request = http.request(
                  'POST',
                  insights_url,
                  headers={"X-Insert-Key": insights_license_key,
                       "Content-Type": "application/json",
                       "Accept": "application/json"},
                  body=encoded_data)
        if debug:
            print(request.status)
            print(request.data)
            print(json.dumps(nroutput))
            sys.stdout.flush()
    except IOError as err:
        if debug:
            if hasattr(err, 'code'):
                print("HTTP Error Code {} received from Insights. Passing.".format(err.code))
            if hasattr(err, 'reason'):
                print("Error Reason: {}".format(err.reason))
            print(json.dumps(nroutput))
        pass # i know, i don't like it either, but we don't want a single failed connection to break the loop.

try:
    print("New Relic Of Things - Temperature Sensor (CTRL+C to exit)")
    time.sleep(2)
    while True:
        start = time.time()
        nroutput['eventType'] = 'PiTemperatureSensorEvent'
        nroutput['sensorLocation'] = sensor_location
        nroutput['temperature_c'] = sensor.get_temperature()
        nroutput['temperature_f'] = sensor.get_temperature(W1ThermSensor.DEGREES_F)
        if debug:
            print("Temperature: {} Temp (F): {} Temp (C): {}".format(nroutput['temperature_c'], nroutput['temperature_f']))
        add_to_insights()
        nroutput = {}
        sys.stdout.flush()

        # Delay next cycle based on what's left in the interval
        end = time.time()
        timeElapsed = end - start
        if timeElapsed < checkDelay:
            time.sleep(checkDelay - timeElapsed)
        else:
            time.sleep(checkDelay)
except KeyboardInterrupt:
    print("\nQuitting.")
