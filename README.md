# MrRoaboto
This repo is a FB messenger bot service that serves Colorado's Department of Transportation (CDOT) XML feeds for rode closure information and alerts. All of the subdirectories are AWS Lambda functions handling different parts of the bot's functionality.

# Where does MrRoadboto live?
MrRoadboto's page is [here](https://www.facebook.com/roadboto/). These messages go directly to the chat lambda instance for parsing.

# Lambda Functions

## chat
This lambda handles user interaction between FB and the backend. This function only contains messaging logic. 

## digestor
Pulls from CDOT, parses weather information, and put's it in the DB.

