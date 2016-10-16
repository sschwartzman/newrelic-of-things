import sys
import RPi.GPIO as GPIO
import time
import json
import time
import urllib
import urllib2
from sht1x.Sht1x import Sht1x as SHT1x
from pynest.nest import Nest
import nest as newnest

# Required to set these
insights_account = "enter_your_account_id_here"
insights_license_key = "enter_your_insert_key_here"
nest_login = "enter_your_nest_login_here"
nest_pass = "enter_your_nest_password_here"

# Likely don't have to change these, but go for it if you want
debug = False
checkDelay = 30

# Only change these if your pin layout is different
shtDataPin = 23
shtClkPin = 18
PIRPin = 17

# Don't mess with these
yesmotion = nomotion = 0
nroutput = {}
insights_url = "https://insights-collector.newrelic.com/v1/accounts/" + insights_account + "/events"
reserved_words = ['accountId','appId','duration','timestamp','type','YESTERDAY']
sht1x = SHT1x(shtDataPin, shtClkPin, SHT1x.GPIO_BCM)
n = Nest(nest_login, nest_pass)

def convert_c_to_f(temp_c):
    return (temp_c * 1.8) + 32
    
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
            print response.read()
            print response.getcode()
            print json.dumps(nroutput)
            sys.stdout.flush()
        response.close()
    except IOError, err:
        if debug:
            if hasattr(err, 'code'):
                print("HTTP Error Code {} received from Insights. Passing.".format(err.code))
            if hasattr(err, 'reason'):
                print("Error Reason: {}".format(err.reason))      
            print json.dumps(nroutput)
        pass # i know, i don't like it either, but we don't want a single failed connection to break the loop.

try:
    print "New Relic Of Things - PIR, SHT & Nest Test (CTRL+C to exit)"
    time.sleep(2)
    while True:
        start = time.time()
        nroutput['eventType'] = 'LifeOfNRPi'
        nroutput['office_temperature'] = sht1x.read_temperature_C()
        nroutput['office_temperature_f'] = convert_c_to_f(nroutput['office_temperature']) 
        nroutput['office_humidity'] = sht1x.read_humidity()
        nroutput['office_dewpoint'] = sht1x.calculate_dew_point(nroutput['office_temperature'], nroutput['office_humidity'])
        if debug:
            print("Temperature: {} Temp (F): {} Humidity: {} Dew Point: {}".format(nroutput['office_temperature'], nroutput['office_temperature_f'],nroutput['office_humidity'],nroutput['office_dewpoint']))
        try:
            n.login()
            n.get_status()
        except Exception, err:
            if hasattr(err, 'code'):
                print("HTTP Error Code {} received from Nest. Passing.".format(err.code))
            if hasattr(err, 'reason'):
                print("Error Reason: {}".format(err.reason))
            if debug:
                print json.dumps(nroutput)
            pass
        shared = n.status["shared"][n.serial]
        device = n.status["device"][n.serial] 
        structure = n.status["structure"][n.structure_id]
        nroutput['away'] = str(structure['away']) 
        for name, value in shared.iteritems():
            if any(name == aword for aword in reserved_words):
                continue
            if type(value) is not dict:
                nroutput[name] = value    
            if type(value) is bool:
                nroutput[name] = str(value)
        nroutput['fixed_away'] = 'False'   
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PIRPin, GPIO.IN)
        if GPIO.input(PIRPin):
            yesmotion += 1
            nroutput['motion_in_office'] = 'True'
            if structure['away'] == True:
                try:
                    fixaway = newnest.Nest(nest_login, nest_pass)
                    fixaway.structures[0].away = False
                    nroutput['fixed_away'] = 'True'
                except IOError, err:
                    if debug:
                        if hasattr(err, 'code'):
                            print("HTTP Error Code {} received from Nest. Passing.".format(err.code))
                        if hasattr(err, 'reason'):
                            print("Error Reason: {}".format(err.reason))
                        print err.headers
                        print json.dumps(nroutput)
                    pass # i know, i don't like it either, but we don't want a single failed connection to break the loop.
        else:
            nomotion += 1
            nroutput['motion_in_office'] = 'False'
        add_to_insights()
        nroutput = {}
        sys.stdout.flush() 
        
        # Delay next cycle based on what's left in the interval (60s) 
        end = time.time()
        timeElapsed = end - start
        if timeElapsed < checkDelay: 
            time.sleep(checkDelay - timeElapsed)
        else:
            time.sleep(checkDelay) 
except KeyboardInterrupt:
    print ""
    print "Quitting."
    print "{}{}{}".format("Motion WAS detected ", yesmotion, " times") 
    print "{}{}{}".format("Motion NOT detected ", nomotion, " times") 
    GPIO.cleanup()
