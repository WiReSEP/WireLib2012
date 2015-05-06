Wilkommen bei WireLib2012
=========================
WireLib2012 ist ein freies Bibliotheksmanagmentsystem welches in der Verwendung
am Institut für Wissenschaftliches Rechnen der Tu Braunschweig ist. Es wurde im
Rahmen eines Software Entwicklungspraktikum im Jahr 2012 entwickelt.

Anwendungsdetails
-----------------
  * Basiert auf Django
  * Layout ist an das Corporate Design der TU Braunschweig angelehnt
  * Export zu Allegro möglich
  * BibTeX-kompatibel


Beschreibung
------------
Das WireLib2012-Projekt ist ein auf dem Webframework Django basierendes 
Bibliotheksmangementsystem, geschrieben in der Programmiersprache Python. Das
Managementsystem ermöglicht den Verleih von Dokumenten an registrierte Nutzer,
oder auch an Externe bei Angabe eines Bürgen. Der Verleih an registrierte
Nutzer basiert auf Vertrauen, jeder kann zu jedem Zeitpunkt ein Buch als
verliehen markieren. Außerdem ist die Benutzerführung dieses Systems einfach
gehalten, es ist intuitiv benutzbar ohne lange Einarbeitungszeit. Das Layout
entspricht dem Corporate Design der TU Braunschweig. Über integrierte
Funktionen ist es möglich, Backups im BibTeX-Format zu führen, ebenso wie den
Inhalt im ADT-Format an auf Allegro basierenden Datenbanken zu übermitteln. Das
System ist aufgrund von Django und der damit benötigten Relationalen Datenbank
nicht für außerordentlich große Mengen an Dokumenten ausgelegt.


Installation
------------

Die Installation wird für den Apache2 Webserver in Version >= 2.4 auf einem
Ubuntu 14.04 beschrieben. Dazu müssen zunächst die folgenden Abhängigkeiten
installiert werden:

	apt-get install python-django python-flup python-pip \
					apache2 libapache2-mod-wsgi \
					git \
					python-mysqldb mysql

Anschließend kann das Projekt mit git herunter geladen werden. Dabei ist zu
beachten, dass es empfohlen ist WireLib2012 unter */opt* zu installieren wenn
das Projekt in einem anderen Ordner plaziert wird sind evtl. Anpassungen
notwendig.

	cd /opt && git clone https://github.com/WiReSEP/WireLib2012.git

Um den Apache einzurichten sind die folgenden Schritte notwendig:

	a2enmod wsgi
	cd /opt/WireLib2012
	ln -s /opt/WireLib2012/etc/apache.conf \
		/etc/apache2/conf-available/wirelib.conf
	a2enconf wirelib

Für die Mysql Konfiguration sollte zunächst eine Datenbank und ein Nutzer wie
folgt angelegt werden:

	$ mysql --defaults-extra-file=/etc/mysql/debian.cnf
	> CREATE DATABASE wirelib CHARACTER SET utf8 COLLATE utf8_general_ci;
	> CREATE USER 'wirelib' IDENTIFIED BY '<very secret password>';
	> GRANT ALL PRIVILEGES ON wirelib.* TO 'wirelib';

Anschließend muss die wirelib Konfigurationsdatei kopiert und angepasst werden.

	cd /opt/WireLib2012/etc
	cp wirelib.cfg.template wirelib.cfg
	editor wirelib.cfg

Dabei muss die Datenbank Sektion entsprechend der Mysql-Konfiguration angepasst
werden und unter `[global]` in dem Feld `allowed_hosts` alle Hostnamen, Komma
seperiert, eingetragen werden, unter denen WireLib2012 erreichbar sein soll.
Mehr Informationen zu dieser Option sind
[hier](https://docs.djangoproject.com/en/1.6/ref/settings/#allowed-hosts) zu
finden. Wenn die Option `allowed_hosts` fehlerhaft ist bekommt man bei einem
Aufruf der Seite einen HTTP Fehler 400 (bad request).

Um die Datenbank anschließend zu initialisieren und die Tabellen an zu legen
muss noch der folgende Befehl durchgeführt werden:

	cd /opt/WireLib2012/src
	python manage.py syncdb

Dieser Befehl gibt einem auch die Möglichkeit den ersten Nutzer anzulegen.
Um sowohl den Bibtex als auch den Allegro export zu ermöglichen muss dem Nutzer
*www-data* schreibzugriff auf den entsprechenden Ordner gewährt werden, was mit
dem folgenden Befehl möglich ist:

	cd /opt/WireLib2012/
	chmod www-data:www-data -R static/exports

Nach einem Neustart des Webservers ist nun Wirelib auf dem Rechner verfügbar.

	service apache2 restart


Datensicherung und Rückspielen
------------------------------

Zur Datensicherung wird zunächst ein Backup der SQL-Datenbank mit deren eigenen
Mitteln empfohlen. Es gibt aber noch zwei weitere Mechanismen die hier
vorgestellt sein sollen.

### Django dumpdata & loaddata

Django liefert über den `manage.py` Befehl einen Mechanismus bereit mit dem die
Inhalte einzelner Apps Datenbankunabhängig exportiert im JSON-Format exportiert
werden können. Um damit z.B. die Daten der `documents` app zu exportieren, die
alle Informationen zu den Büchern enthält ist der folgende Befehl notwendig:

	./manage.py dumpdata documents > documents.json

Mit diesem Befehl werden die Daten der `documents`-App in die Datei
*documents.json* im JSON-Format exportiert. Um diese Daten an anderer Stelle
wieder zu importieren ist der folgende Befehl notwendig:

	./manage.py loaddata documents.json

Bei diesem Mechanismus ist zu beachten, dass die Daten in `documents` von den
Benutzern abhängen, da Informationen zu den Benutzern gespeichert werden die
mit den Dokumenten gearbeitet haben. Die Nutzer müssen ebenfalls auf dem zu
importierenden System exestieren, sonst schlägt der Import fehl.

### Bibtox export

Der Bibtex-export ist eine Funktion die in der Weboberfläche zur Verfügung
steht. Er dient vor allem dem Export in ein unabhängiges Format und kann nicht
für einen reimport verwendet werden. Nutzen hätte er also vor allem um auf ein
anderes Verwaltungssystem zu welchseln.
