'use strict';

var Insights = require('node-insights');
var ds18b20 = require('ds18b20');
var request = require('request');

var insightsSettings = {
  insertKey: 'REDACTED',
  queryKey: 'REDACTED',
  accountId: 'REDACTED'
}

var polling_interval = 10000;
var taking_temp = false;
var debug_on = false;

function debugLog(msg) {
  if(debug_on) {
    console.log(msg);
  }
}

var insights = new Insights(insightsSettings);
var weatherInsightsQuery = 'SELECT%20latest(%60custom.temperature%60),%20latest(%60custom.humidity%60),%20latest(%60custom.summary%60)%20FROM%20SyntheticCheck%20where%20%60custom.temperature%60%20IS%20NOT%20NULL';
var weatherQueryOptions = {
  url: 'https://insights-api.newrelic.com/v1/accounts/' + insightsSettings['accountId'] + '/query?nrql=' + weatherInsightsQuery,
  headers: {
    'Accept': 'application/json',
    'X-Query-Key': insightsSettings['queryKey']
  }
};

console.log('New Relic Pi Zero Thingy reporting for duty, sir/madam.');
debugLog('Debug logging is enabled.');

setInterval(function() {
  if(!taking_temp) {
    taking_temp = true;
    ds18b20.sensors(function(err, ids) {
      if (err) {
        debugLog("Can not get sensor IDs, error: " + err);
      }
      debugLog('Sensor IDs', ids);
      ids.forEach(function(id) {
        ds18b20.temperature(id, function(err, value) {
          if (err) {
            debugLog("Can not get temperature for sensor ID " + id + ", error: " + err);
          } else {
            debugLog("Current temperature is " + value + " Degrees Celsius");
            var fvalue = value * 9 / 5 + 32;
            debugLog("Current temperature is " + fvalue + " Degrees Fahrenheit");
            var thisEvent = {
              eventType: 'PiZeroEvent',
              currTempC: value,
              currTempF: fvalue
            };
            request(weatherQueryOptions, function(error, response, body) {
              if (!error && response.statusCode == 200) {
                var data = JSON.parse(body);
                if (data['results'] != null) {
                  thisEvent['darksky.temperature'] = data['results'][0]['latest'];
                  thisEvent['darksky.humidity'] = data['results'][1]['latest'];
                  thisEvent['darksky.summary'] = data['results'][2]['latest'];
                }
              } else {
                debugLog('Query to Insights failed.');
                debugLog('Response Error: ' + error);
                debugLog('Response Code: ' + response.statusCode);
                debugLog('Response Body: ' + body);
              }
              debugLog('Sending to Insights: ' + thisEvent);
              insights.add(thisEvent);
            });
          }
        });
      });
    });
    taking_temp = false;
  }
}, polling_interval);
