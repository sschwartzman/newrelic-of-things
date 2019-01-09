import sys
import json
import time
import urllib
import urllib3
import certifi
from flatten_json import flatten

# Required to set these
insights_account = "enter_your_account_id_here"
insights_license_key = "enter_your_insert_key_here"
octoprint_api_key = "enter_your_octoprint_api_key_here"
octoprint_host_url = "http://octopi.local"

# Likely don't have to change these, but go for it if you want
debug = False
checkDelay = 30

# Don't mess with these
insights_url = "https://insights-collector.newrelic.com/v1/accounts/" + insights_account + "/events"
reserved_words = ['accountId','appId','duration','timestamp','type','YESTERDAY']
nroutput = {}

http = urllib3.PoolManager(
    cert_reqs='CERT_REQUIRED',
    ca_certs=certifi.where())

def get_from_octoprint(command):
    octoprint_full_url = octoprint_host_url + "/api/" + command + "?history=false"
    try:
        request = http.request(
                  'GET',
                  octoprint_full_url,
                  headers={"X-Api-Key": octoprint_api_key,
                       "Content-Type": "application/json",
                       "Accept": "application/json"})
        if debug:
            print(request.status)
            print(request.data)
            print(json.dumps(nroutput))
            sys.stdout.flush()
        return json.loads(request.data.decode('utf-8'))
    except IOError as err:
        if debug:
            if hasattr(err, 'code'):
                print("HTTP Error Code {} received from Insights. Passing.".format(err.code))
            if hasattr(err, 'reason'):
                print("Error Reason: {}".format(err.reason))
            print(json.dumps(nroutput))
        pass # i know, i don't like it either, but we don't want a single failed connection to break the loop.
        return {}

def add_to_insights():
    try:
        encoded_data = json.dumps(flatten(nroutput, '.')).encode('utf-8')
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
    print("New Relic Of Things - OctoPrint (CTRL+C to exit)")
    time.sleep(2)
    while True:
        start = time.time()
        nroutput['eventType'] = 'OctoPrintEvent'
        nroutput['job'] = get_from_octoprint('job')
        nroutput['printer'] = get_from_octoprint('printer')
        if debug:
            print("JSON From OctoPrint: {}".format(json.dumps(nroutput)))
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
