#!/bin/bash
apt-get install python-django python-flup python-pip python-mysqldb libapache2-mod-wsgi
a2enmod wsgi

ln -s "$(pwd)/etc/apache.conf" /etc/apache2/conf-available/wirelib.conf
a2enconf wirelib
service apache2 restart

chmod www-data:www-data -R static/exports
