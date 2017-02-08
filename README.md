# Mr.Roadboto
A low-bandwidth and easy to use Facebook chat bot that serves Colorado's Department of Transportation (CDOT) alerts for I70 road-closures affecting major ski resorts. You can read about the motivation [here](https://medium.com/@antsankov/domo-arigato-mr-roadboto-pt-1-introducing-the-problem-b0d44e384dc#.tcsq9nrs4).

![img](http://imgur.com/3EEgDfe.png)

## Where does Mr.Roadboto live?
MrRoadboto's Facebook page is [here](https://www.facebook.com/roadboto/). These messages go directly to AWS for parsing.

## What Resorts does Mr.Roadboto support?
* Vail
* Winter Park
* Arapahoe Basin
* Copper Mountain
* Keystone
* Breckenridge

## Architecture
Mr.Roadboto is designed to be both elastic and ephemeral. He is independently made up of multiple AWS Lambda functions for user interaction and data gathering.
* CDOT only allows me to query their system once every two minutes, perfect for a Lambda function.
* The highly variable demand for chat bot interaction also lends itself well to a Lambda.
* A high performance Redis cache sits between them for rapid data extraction.

![Architecture Diagram](http://i.imgur.com/gNA8DbP.jpg)

## Lambda Functions

### `/chat`
Handles user interaction between FB and the backend. This function only contains messaging logic. It uses the [Claudia Bot Builder](https://github.com/claudiajs/claudia-bot-builder) library to handle deployment and interaction with Facebook messenger

### `/digestor`
Launched by Cloudwatch Events every five minutes. Pulls from CDOT, parses weather information, and puts it in the DB.
