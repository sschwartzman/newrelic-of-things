import codecs
import csv
import json
import requests

airurl = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airlines.dat"
airin = requests.get(airurl).iter_lines()
airout = []

aircsv = csv.reader(codecs.iterdecode(airin, 'utf-8'), delimiter=',', strict=True)
for airline in aircsv:
    if airline[4] != "\\N" and airline[4] != "N/A" and airline[4] != "":
        thisout = {}
        thisout['ICAO'] = airline[4]
        thisout['Airline'] = airline[1]
        thisout['Country'] = airline[6]
        thisout['Callsign'] = airline[5]
        airout.append(thisout)

print (json.dumps(airout, sort_keys=True, indent=4, separators=(',', ': ')))
