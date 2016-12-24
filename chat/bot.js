var botBuilder = require('claudia-bot-builder'),
  fbTemplate = botBuilder.fbTemplate;

const redisOptions = {
  host: process.env.cache_ip,
  port: "6379"
};

var redis = require('redis'),
  client = redis.createClient(redisOptions);

const resorts = ['Arapahoe Basin', 'Breck', 'Keystone', 'Vail', 'Copper Mountain'];

module.exports = botBuilder(request => {
  console.log("Req test: " + request.text);
  // if it's in a resort
  if (resorts.indexOf(request.text) >= 0){
    console.log('Hit it');
    var vail = client.get('hash', (err, value) => { 
      return value;
    });
    console.log(typeof(vail));
    console.log(vail);
    console.log(vail.toString());
    message = new fbTemplate.Text(vail);
    return message.get();
  } else {
    message = new fbTemplate.Text('Which resort do you want to know about?');
    resorts.forEach(function(resort){
      message.addQuickReply(resort, resort);
    });
    return message.get();    
  } 
});
