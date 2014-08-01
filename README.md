Wilkommen bei WireLib2012
=========================
WireLib2012 ist ein freies Bibliotheksmanagmentsystem.

Anwendungsdetails
-----------------
  * Basiert auf Django
  * Layout entspricht Corporate Design der TU Braunschweig
  * Export zu Allegro möglich
  * BibTeX-kompatibel

Anforderungen
-------------
  * Django 1.5
  * mysql oder sqlite
  * Webserver
  * *optional:* git

Installation
------------
Für die Installation folgen Sie bitte den Schritten im Wiki.

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
