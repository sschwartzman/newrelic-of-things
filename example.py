import sys
import RPi.GPIO as GPIO
import time
import json
import time
import urllib
import urllib2

# Sht1x and pynest are available on pypi.python.org:
# Sht1x: https://pypi.python.org/pypi/rpiSht1x/1.2
# PyNest: https://pypi.python.org/pypi/PyNest/0.1a3
from sht1x.Sht1x import Sht1x as SHT1x
from pynest.nest import Nest

# Replace <your_account> with your account number
insights_url = "https://insights.newrelic.com/beta_api/accounts/<your_account>/events"
# Replace with your insights "Insert Key": https://insights.newrelic.com/accounts/<your_account>/manage/api_keys
insights_license_key = "insert_your_insights_insert_key_here"
debug = False
shtDataPin = 23
shtClkPin = 18
PIRPin = 17
checkDelay = 10
yesmotion = nomotion = 0
nroutput = {}
reserved_words = ['accountId','appId','duration','timestamp','type','YESTERDAY']

GPIO.setmode(GPIO.BCM)
sht1x = SHT1x(shtDataPin, shtClkPin, SHT1x.GPIO_BCM)
n = Nest("test@gmail.com", "testpassword")

def add_to_insights():
    try:
        opener = urllib2.build_opener(urllib2.HTTPHandler(), urllib2.HTTPSHandler())
        request = urllib2.Request(insights_url)
        request.add_header("X-Insert-Key", insights_license_key)
        request.add_header("Content-Type","application/json")
        request.add_header("Accept","application/json")
        response = opener.open(request, json.dumps(nroutput))
        if debug:
            print request.get_full_url()
            print response
            print response.getcode()
            print json.dumps(nroutput)
            sys.stdout.flush()
        response.close()
    except IOError, err:
        if debug:
            print json.dumps(nroutput)
        if hasattr(err, 'code'):
            print("HTTP Error Code {} received from Insights. Passing.".format(err.code))
        if hasattr(err, 'reason'):
            print("Error Reason: {}".format(err.reason))     
        pass # i know, i don't like it either, but we don't want a single failed connection to break the loop.

try:
    print "New Relic Of Things - PIR, SHT & Nest Test (CTRL+C to exit)"
    time.sleep(2)
    while True:
        start = time.clock()
        nroutput['eventType'] = 'LifeOfNRPi'
        try:
            n.login()
            n.get_status()
        except IOError, err:
            if hasattr(err, 'code'):
                print("HTTP Error Code {} received from Nest. Passing.".format(err.code))
            if hasattr(err, 'reason'):
                print("Error Reason: {}".format(err.reason))
            if debug:
                print json.dumps(nroutput)
            pass
        shared = n.status["shared"][n.serial]
        device = n.status["device"][n.serial] 
        #shared.update(device)
        for name, value in shared.iteritems():
            if any(name == aword for aword in reserved_words):
                continue
            if type(value) is not dict:
                nroutput[name] = value    
            if type(value) is bool:
                nroutput[name] = str(value)
        GPIO.setup(PIRPin, GPIO.IN)
        if GPIO.input(PIRPin):
            yesmotion += 1
            nroutput['motion_in_office'] = 'true'
        else:
            nomotion += 1
            nroutput['motion_in_office'] = 'false'
        nroutput['office_temperature'] = sht1x.read_temperature_C()
        nroutput['office_humidity'] = sht1x.read_humidity()
        nroutput['office_dewpoint'] = sht1x.calculate_dew_point(nroutput['office_temperature'], nroutput['office_humidity'])
        # print("Temperature: {} Temp (F): {} Humidity: {} Dew Point: {}".format(temperature, temp_f, humidity, dewPoint))
        add_to_insights()
        nroutput = {}
        sys.stdout.flush() 
        
        # Delay next cycle based on what's left in the interval (60s) 
        end = time.clock()
        timeElapsed = end - start
        time.sleep(checkDelay - timeElapsed)
        
except KeyboardInterrupt:
    print ""
    print "Quitting."
    print "{}{}{}".format("Motion WAS detected ", yesmotion, " times") 
    print "{}{}{}".format("Motion NOT detected ", nomotion, " times") 
    GPIO.cleanup()
