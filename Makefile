update-chat:
	 export AWS_PROFILE=claudia
	 cd chat/ && \
	 jshint *.js && \
	 claudia update 

digest-local:
	python digestor/digestor.py

digest-remote:
	python digestor/digestor.py --live=True
