import sys
import time
import json
import nest
import urllib
import urllib3
import certifi

# Required to set these
insights_account = "enter_your_account_id_here"
insights_license_key = "enter_your_insert_key_here"
nest_login = "enter_your_nest_login_here"
nest_pass = "enter_your_nest_password_here"
access_token_cache_file = 'nest.json'

# Likely don't have to change these, but go for it if you want
debug = True
checkDelay = 30

# Don't mess with these
nroutput = {}
insights_url = "https://insights-collector.newrelic.com/v1/accounts/" + insights_account + "/events"
reserved_words = ['accountId','appId','duration','timestamp','type','YESTERDAY']
napi = nest.Nest(client_id=client_id, client_secret=client_secret, access_token_cache_file=access_token_cache_file)
http = urllib3.PoolManager(
    cert_reqs='CERT_REQUIRED',
    ca_certs=certifi.where())

if napi.authorization_required:
    print('Go to ' + napi.authorize_url + ' to authorize, then enter PIN below')
    if sys.version_info[0] < 3:
        pin = raw_input("PIN: ")
    else:
        pin = input("PIN: ")
    napi.request_token(pin)

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
    print("New Relic Of Things - Nest (CTRL+C to exit)")
    time.sleep(2)
    while True:
        start = time.time()

        for structure in napi.structures:
            for device in structure.thermostats:
                nroutput = device._device
                nroutput['eventType'] = 'NestThermostatEvent'
                add_to_insights()

        nroutput = {}
        sys.stdout.flush()

        # Delay next cycle based on what's left in the interval (30s)
        end = time.time()
        timeElapsed = end - start
        if timeElapsed < checkDelay:
            time.sleep(checkDelay - timeElapsed)
        else:
            time.sleep(checkDelay)
except KeyboardInterrupt:
    print("")
    print("Quitting.")
