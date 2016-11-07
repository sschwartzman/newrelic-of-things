import sys
import time
import json
import time
import urllib
import urllib2

# Required to set these
insights_account = "enter_your_account_id_here"
insights_license_key = "enter_your_insert_key_here"

# Point to where you're running dump1090 (host & port)
dump1090_host = "localhost"
dump1090_port = "8080"

# Likely don't have to change these, but go for it if you want
debug = False
checkDelay = 10

# Old Dump1090 URL
#dump1090_url = "http://" + dump1090_host + ":" + dump1090_port + "/data.json"
# New Dump10909 (FlightAware version) URL
dump1090_url = "http://" + dump1090_host + ":" + dump1090_port + "/dump1090-fa/data/aircraft.json"

# Don't mess with these
insights_url = "https://insights-collector.newrelic.com/v1/accounts/" + insights_account + "/events"
nroutput = {}
reserved_words = ['accountId','appId','duration','timestamp','type','YESTERDAY']
airplanes = 0

with open('airlines.json') as data_file:    
    airlines = json.load(data_file)
def merge_two_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z

def add_to_insights(thedata):
    try:
        opener = urllib2.build_opener(urllib2.HTTPHandler(), urllib2.HTTPSHandler())
        request = urllib2.Request(insights_url)
        request.add_header("X-Insert-Key", insights_license_key)
        request.add_header("Content-Type","application/json")
        request.add_header("Accept","application/json")
        response = opener.open(request, json.dumps(thedata))
        if debug:
            print json.dumps(thedata)
            print request.get_full_url()
            print response.read()
            print response.getcode()
            sys.stdout.flush()
        response.close()
    except IOError, err:
        print err
        if debug:
            if hasattr(err, 'code'):
                print("HTTP Error Code {} received from Insights. Passing.".format(err.code))
            if hasattr(err, 'reason'):
                print("Error Reason: {}".format(err.reason))      
            print json.dumps(thedata)
        pass # i know, i don't like it either, but we don't want a single failed connection to break the loop.

try:
    print "New Relic Insights sink for Dump1090 (CTRL+C to exit)"
    time.sleep(2)
    while True:
        start = time.time()
        try:
            dump1090_data = json.load(urllib2.urlopen(dump1090_url))['aircraft']
            # print dump1090_data 
            # print "{}{}".format("Number of airplane records: ", len(dump1090_data))
            for i in range(0, len(dump1090_data)):
                dump1090_data[i]['commercial'] = 'false'
                dump1090_data[i]['eventType'] = 'Dump1090'
                if 'flight' in dump1090_data[i].keys():
                    for airline in airlines:
                        if dump1090_data[i]['flight'][:3] == airline['ICAO']:
                            dump1090_data[i] = merge_two_dicts(dump1090_data[i], airline)
                            dump1090_data[i]['commercial'] = 'true'
                            break
                    airplanes += 1
            add_to_insights(dump1090_data) 
            sys.stdout.flush() 
        except Exception, err:
            if hasattr(err, 'code'):
                print("HTTP Error Code {} received from Dump1090. Passing.".format(err.code))
            if hasattr(err, 'reason'):
                print("Error Reason: {}".format(err.reason))
            if debug:
                print json.dumps(dump1090_data)
            pass
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
    print "{}{}".format("Number of airplane events: ", airplanes)
