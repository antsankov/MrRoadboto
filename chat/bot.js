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

const welcome = 'Hello. I can tell you if I70 is open between the major Colorado ski resorts and the Front Range. Select a resort from one of the buttons below.';

const resorts = [
  'Vail',
  'Copper Mountain', 'Breckenridge', 
  'Keystone', 'Arapahoe Basin',
  'Winter Park'
];

//takes in a string and returns a FB version with all of the buttons.
function MakeFB(content){
  message = new fbTemplate.Text(content);
  resorts.forEach(function(resort){
    message.addQuickReply(resort, resort);
  });
  return message.get(); 
}

module.exports = botBuilder(request => {
  console.log('req: ' + request.text);
  
  if (request.text === 'Get Started'){
    return MakeFB(welcome);
  }
  // if it's in a resort
  if (resorts.indexOf(request.text) >= 0){ 
    return client.getAsync(request.text).then((res,err) => {
      if (err) {
        console.error(err);
        return MakeFB('There was an error! Oops.');
      }  
      return MakeFB(res);
    });
  } else {
    return MakeFB('Which resort do you need I70 info about?');
  } 
});
