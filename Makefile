update-chat:
	 cd chat/ && \
	 jshint *.js && \
	 claudia update --profile claudia 

digest-local:
	python digestor/digestor.py

digest-remote:
	python digestor/digestor.py --live=True
