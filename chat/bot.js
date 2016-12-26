var botBuilder = require('claudia-bot-builder'),
  fbTemplate = botBuilder.fbTemplate;

const redisOptions = {
  host: process.env.hostname,
  port: process.env.port
};

var bluebird = require('bluebird');
var redis = require('redis');
bluebird.promisifyAll(redis.RedisClient.prototype); 
client = redis.createClient(redisOptions);

const resorts = [
  'Vail',
  'Copper Mountain', 'Breckenridge', 
  'Keystone', 'Arapahoe Basin'
];

module.exports = botBuilder(request => {
  console.log('Req test: ' + request.text);
  // if it's in a resort
  if (resorts.indexOf(request.text) >= 0){ 
    return client.getAsync(request.text).then((res,err) => {
      if (err) {
        console.log(err);
        return 'There was an error! Oops.';
      }  
      return res;
    });
  } else {
    message = new fbTemplate.Text('Which resort do you need road info about?');
    resorts.forEach(function(resort){
      message.addQuickReply(resort, resort);
    });
    return message.get(); 
  } 
});
