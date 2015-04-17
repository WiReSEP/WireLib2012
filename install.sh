#!/bin/bash
aptitude install python-django python-flup python-pip
pip install -r requirements.txt

ln -s etc/apache2.conf /etc/apache2/conf.available/wirelib.conf
a2enconf wirelib
service apache2 restart
