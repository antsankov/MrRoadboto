update-chat:
	 cd chat/ && \
	 jshint *.js && \
	 claudia update --profile claudia 

redis:	
	docker run --name RoadbotoRedis -d -p 6379:6379 redis 

redis-cli:
	docker exec -it RoadbotoRedis redis-cli

digest-local:
	python digestor/digestor.py --local

digest-remote:	
	python digestor/digestor.py

update-digestor:
	zip -d ../DigestorDeploy.zip digestor.py
	zip -j ../DigestorDeploy.zip digestor/digestor.py 
	aws lambda update-function-code --function-name Digestor --zip-file fileb://../DigestorDeploy.zip --profile MrRoadboto --region us-east-1
