FROM ubuntu:14.04
MAINTAINER Theodor van Nahl <theo_dev@van-nahl.org>

RUN apt-get update && apt-get install -y \
	python-django python-flup python-pip \
	apache2 libapache2-mod-wsgi libapache2-mod-xsendfile
RUN a2enmod wsgi
RUN a2enmod xsendfile

COPY requirements.txt /opt/requirements.txt
RUN pip install -r /opt/requirements.txt

# Manually set up the apache environment variables
ENV APACHE_RUN_USER www-data
ENV APACHE_RUN_GROUP www-data
ENV APACHE_LOG_DIR /var/log/apache2
ENV APACHE_LOCK_DIR /var/lock/apache2
ENV APACHE_PID_FILE /var/run/apache2.pid 
ENV PYTHONPATH /opt/WireLib2012/src

# Installation von Wirelib
COPY . /opt/WireLib2012

#RUN python /opt/WireLib2012/src/wirelib/manage.py syncdb --noinput
#RUN python /opt/WireLib2012/src/wirelib/manage.py loaddata /opt/WireLib2012/documents.json

COPY etc/apache.conf /etc/apache2/conf-available/wirelib.conf
RUN a2enconf wirelib

EXPOSE 80

CMD /bin/bash
