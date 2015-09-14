#SHELL := /bin/bash
TODAY := $(shell date +"%Y-%M-%d-%H%M%S")

backup:
	@mkdir -p ../dbbackup
	./manage.py dumpdata --indent=2 > ../dbbackup/backup-full-$(TODAY).json
