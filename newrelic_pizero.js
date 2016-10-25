var Insights = require('node-insights');
var ds18b20 = require('ds18b20');

var insights = new Insights({
  insertKey: 'REDACTED!',
  accountId: 'REDACTED!'
});

var polling_interval = 10000;
var taking_temp = false;
var debug_on = false;

function debugLog(msg) {
  if(debug_on) {
    console.log(msg);  
  }
}

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
            insights.add({
              eventType: 'PiZeroEvent',
              currTempC: value,
              currTempF: fvalue
            });
          }
        });
      });
    });
    taking_temp = false;
  }
}, polling_interval);
