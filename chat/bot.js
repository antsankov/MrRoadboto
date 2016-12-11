var botBuilder = require('claudia-bot-builder'),
  fbTemplate = botBuilder.fbTemplate;

const resorts = ['A-basin', 'Breck', 'Keystone'];

module.exports = botBuilder(message => {
  if (message.type === 'facebook') {
    message = new fbTemplate.Text('Which resort do you want to know about?');
    resorts.forEach(function(resort){
      message.addQuickReply(resort, resort.toUpperCase());
    });
    return message.get();
  }
});
