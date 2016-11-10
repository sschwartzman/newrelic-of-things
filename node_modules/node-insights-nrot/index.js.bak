'use strict';

var _ = require('lodash');
var request = require('request');
var logger = console;

/**
 * Insights
 * @constructor
 * @param {Object} config - configuration object
 * @param {string} config.accountId - your newrelic insights account id
 * @param {string} config.insertKey - your newrelic insert key
 * @param {string} config.queryKey - your newrelic query key
 * @param {integer} [config.timerInterval=10000] - the timer interval (in milliseconds) that is used for sending data
 * @param {integer} [config.maxPending=1000] - the maximum number of items held in the queue before being sent
 * @param {string} [config.defaultEventType='data'] - when adding data, you can specify the eventType that is sent to New Relic.  If you don't specify the eventType, the defaultEventType is used.
 * @param {boolean} [config.enabled=true] - enable/disable the sending of insights data.
 *
 * @example
 *    new Insights({
 *      accountId: '...',
 *      insertKey: '...',
 *      queryKey: '...',
 *    });
 *
 */
function Insights(config){

  this.config = _.assign({
    accountId: null,
    enabled: true,
    logger: logger,
    insertKey: '',
    queryKey: '',
    timerInterval: 10000,
    maxPending: 1000,
    shouldFinish: false,
    defaultEventType: 'data'
  }, config);

  if(_.isEmpty(this.config.accountId)){
    throw new Error('Missing account ID');
  }

  this.data = [];
  this.timerId = null;
  this.timerCallback = _.bind(this.send, this);
  this.urlPathPrefix = '/v1/accounts/' + this.config.accountId + '/';

  Object.defineProperty(this, 'enabled', {
    get: function () {
      return this.config.enabled;
    },
    set: function(val){
      this.config.enabled = val;
    }
  });

  Object.defineProperty(this, 'queryKey', {
    get: function () {
      return this.config.queryKey;
    },
    set: function(val){
      this.config.queryKey = val;
    }
  });

  Object.defineProperty(this, 'insertKey', {
    get: function () {
      return this.config.insertKey;
    },
    set: function(val){
      this.config.insertKey = val;
    }
  });

}

Insights.collectorBaseURL = 'https://insights-collector.newrelic.com';
Insights.queryBaseURL = 'https://insights-api.newrelic.com';


/**
* Start the timer that will send insights after some interval of time
* this is called implicitly when data is added via the add method
*/
Insights.prototype.start = function(){
  if (!this.timerId){
    this.timerId = setInterval(this.timerCallback, this.config.timerInterval);
  }
};

/**
* Stop the timer that will send insights after some interval of time
* this is called implicitly when the amount of data exceeds maxPending and the queue is sent
*/
Insights.prototype.stop = function(){
  if (this.timerId){
    clearInterval(this.timerId);
    this.timerId = null;
  }
};

/**
* Stop the timer after flushing.
*/
Insights.prototype.finish = function(){
  if (this.timerId){
    this.shouldFinish = true;
  }
};

/**
 * Send accumulated insights data to new relic (if enabled)
 */
Insights.prototype.send = function(){
  var that = this;
  var bodyData;
  if (this.config.enabled && this.data.length > 0){
    bodyData = this.data;
    this.data = [];
    request({
      method: 'POST',
      json: true,
      headers: {
        'X-Insert-Key': this.config.insertKey
      },
      url: (Insights.collectorBaseURL + this.urlPathPrefix + 'events'),
      body: bodyData
    }, function(err, res, body){
      if (err){
        that.config.logger.error('Error sending to insights', err);
      } else if (res){
        that.config.logger.log('Insights response', res.statusCode, body);
      }

      if (that.shouldFinish) {
        that.stop();
        that.shouldFinish = false;
      }
    });
  }
};

function reducer(prefix, logger){
  return function(insight, value, key){
    if (_.isString(value) || _.isNumber(value)){
      insight[prefix + key] = value;
    } else if (_.isPlainObject(value) || _.isArray(value)){
      _.reduce(value, reducer(prefix + key + '.', logger), insight);
    } else if (_.isBoolean(value) || _.isDate(value)){
      insight[prefix + key] = value.toString();
    } else {
      //ignore functions, nulls, undefineds
      logger.warn('not reducing', prefix, key, value);
    }
    return insight;
  };
}

/**
* Add insights data to the queue.
* It is sent when the queue reaches a max size or a period of time has elapsed
* @param {object} data - data to flatten and send to insights
* @param {string} [eventType] - event type to associate with data
*/
Insights.prototype.add = function(data, eventType){
  var insight;

  if (_.isEmpty(this.config.insertKey)){
    throw new Error('Missing insert key');
  }

  insight = _.reduce(data, reducer('', this.config.logger), {
    'eventType': eventType || this.config.defaultEventType
  });

  if (insight.timestamp === undefined) {
    insight.timestamp = Date.now();
  }

  this.config.logger.log('Insights data', insight);
  this.data.push(insight);

  if (this.data.length >= this.config.maxPending){
    this.stop();
    this.send();
  } else {
    this.start();
  }
};

/**
 * Build a nrql query string
 * @param {object} params - object containing key/values of nrql query
 * @example
 *    nrql = insights.nrql({
 *      select: 'uniqueCount(session)',
 *     from: 'PageView',
 *     since: '1 week ago',
 *     until: '1 day ago',
 *     timeseries: '1 hour'
 *   });
 *   insights.query(nrql);
 */
Insights.prototype.nrql = function(params) {
  var nrql;

  if (!params){
    throw new Error('Missing nrql parameters');
  }

  if(_.isString(params)) {
    //nrql string was already constructed?
    return params;
  }

  if(!params.select) {
    throw new Error('Parameters must include :select');
  }
  if(!params.from) {
    throw new Error('Parameters must include :from');
  }

  nrql = 'SELECT ' + params.select;
  nrql += ' FROM ' + params.from;
  if(params.where) {
    nrql += ' WHERE ' + this.where(params.where);
  }
  if(params.since) {
    nrql += ' SINCE ' + params.since;
  }
  if(params.until) {
    nrql += ' UNTIL ' + params.until;
  }
  if(params.facet) {
    nrql += ' FACET ' + params.facet;
  }
  if(params.timeseries) {
    nrql += ' TIMESERIES ' + params.timeseries;
  }
  if(params.limit) {
    nrql += ' LIMIT ' + params.limit;
  }
  if(params.compare) {
    nrql += ' COMPARE WITH ' + params.compare;
  }

  return nrql;
};

/**
 * nrql where clause builder
 */
Insights.prototype.where = function(clause) {
  var i, x, key, value, segment, quotedValues;
  var quote = function(value) { return "'" + value + "'"; };
  var clauses = [];
  var segments = [];

  if(!clause) {
    return null;
  }

  if(_.isString(clause)) {
    return '(' + clause + ')';
  } else if(_.isArray(clause)) {
    for(i = 0; i < clause.length; i++) {
      clauses.push(this.where(clause[i]));
    }
    return clauses.join(' AND ');
  }

  for(key in clause) {
    if(clause.hasOwnProperty(key)) {
      value = clause[key];
      segment = '';

      if(_.isArray(value)) {
        quotedValues = [];
        for(i = 0; i < value.length; i++) {
          x = value[i];
          if(!_.isNumber(x)) {
            x = quote(x);
          }
          quotedValues.push(x);
        }
        segment += key + ' IN (';
        segment += quotedValues.join(',');
        segment += ')';
      } else {
        if (!_.isNumber(value)) {
          value = quote(value);
        }
        segment += key + ' = ' + value;
      }
      segments.push(segment);
    }
  }

  if(segments.length > 0) {
    return '(' + segments.join(' AND ') + ')';
  }

  return null;
};

/**
 * Execute a nrql query
 * @param {object|string} query - query object to build and execute or query string to execute
 * @param {function} done - callback
 */
Insights.prototype.query = function(query, done) {
  var url;

  if (_.isEmpty(this.config.queryKey)){
    throw new Error('Missing query key');
  }

  query = this.nrql(query);
  try {
    decodeURIComponent(query);
  } catch(ex) {
    query = encodeURI(query);
  }

  url = Insights.queryBaseURL + this.urlPathPrefix + 'query?nrql=' + query;

  request({
    method: 'GET',
    json: true,
    headers: {
      'X-Query-Key': this.config.queryKey
    },
    url: url
  }, function(err, res, body){
    done(err, body);
  });

};

module.exports = Insights;
