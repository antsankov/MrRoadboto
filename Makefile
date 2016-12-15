update-chat:
	 cd chat/ && \
	 jshint *.js && \
	 claudia update --profile claudia 

redis:	
	docker run --name RoadbotoRedis -d -p 6379:6379 redis 

redis-cli:
	docker exec -it RoadbotoRedis redis-cli

digest-local:
	python digestor/digestor.py

digest-remote:	
	python digestor/digestor.py --live=True
