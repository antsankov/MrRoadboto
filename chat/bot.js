var botBuilder = require('claudia-bot-builder'),
  fbTemplate = botBuilder.fbTemplate;

const redisOptions = {
  host: process.env.cache_ip,
  port: "6379"
};

var bluebird = require('bluebird');
var redis = require('redis');
bluebird.promisifyAll(redis.RedisClient.prototype); 
client = redis.createClient(redisOptions);

const resorts = ['Arapahoe Basin', 'Breck', 'Keystone', 'Vail', 'Copper Mountain'];

module.exports = botBuilder(request => {
  console.log("Req test: " + request.text);
  // if it's in a resort
  if (resorts.indexOf(request.text) >= 0){ 
    return client.getAsync(request.text).then(res => {
      console.log(res);
      return res;
    }); 
  } else {
    message = new fbTemplate.Text('Which resort do you want to know about?');
    resorts.forEach(function(resort){
      message.addQuickReply(resort, resort);
    });
    return message.get(); 
  } 
});
