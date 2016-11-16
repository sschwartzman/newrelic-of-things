'use strict';

var ds18b20 = require('ds18b20');
var Insights = require('node-insights-nrot');
var os = require('os');
var request = require('request');
var debug = require('debug')('nrot');

var insights_settings = {
    insertKey: '0vSzR1h65H8I_Yzg757fuC6pkhjqnekW',
    queryKey: 'KDIGhtIYsUUpShgOu4xCiBITiqkRsRBv',
    accountId: '1469724'
}

var polling_interval = 10000;
var pizero_hostname = os.hostname() || 'PiZero-DefaultHost';

var insights = new Insights(insights_settings);
var weather_insights_query = 'SELECT%20latest(%60custom.temperature%60),%20latest(%60custom.humidity%60),%20latest(%60custom.summary%60)%20FROM%20SyntheticCheck%20where%20%60custom.temperature%60%20IS%20NOT%20NULL';
var weather_query_options = {
    url: 'https://insights-api.newrelic.com/v1/accounts/' + insights_settings['accountId'] + '/query?nrql=' + weather_insights_query,
    headers: {
        'Accept': 'application/json',
        'X-Query-Key': insights_settings['queryKey']
    }
};

console.log('New Relic Pi Zero Thingy reporting for duty, sir/madam.');
debug('Debug logging is enabled.');

var taking_temp = false;

setInterval(function () {
    if (!taking_temp) {
        taking_temp = true;
        ds18b20.sensors(function (err, ids) {
            if (err) {
                console.log("Can not get sensor IDs: " + err);
                taking_temp = false;
                return;
            }
            debug('Sensor ID: ' + ids[0]);
            var temp_c = ds18b20.temperatureSync(ids[0]);
            debug("Current temperature is " + temp_c + " Degrees Celsius");
            var temp_f = temp_c * 9 / 5 + 32;
            debug("Current temperature is " + temp_f + " Degrees Fahrenheit");
            var this_event = {
                eventType: 'PiZeroEvent',
                currTempC: temp_c,
                currTempF: temp_f,
                hostname: pizero_hostname
            };
            request(weather_query_options, function (error, response, body) {
                if (!error && response.statusCode == 200) {
                    var data = JSON.parse(body);
                    if (data['results'] != null) {
                        this_event['darksky.temperature'] = data['results'][0]['latest'];
                        this_event['darksky.humidity'] = data['results'][1]['latest'];
                        this_event['darksky.summary'] = data['results'][2]['latest'];
                    }
                } else {
                    console.log('Query to Insights failed.');
                    console.log('Run with debug for details.');
                    debug('Query to Insights failed.');
                    debug('Response Error: ' + error);
                    debug('Response Code: ' + response.statusCode);
                    debug('Response Body: ' + body);
                }
                debug('Sending to Insights: ' + JSON.stringify(this_event));
                insights.add(this_event);
                taking_temp = false;
            });
        });
    }
}, polling_interval);
