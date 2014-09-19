#vim: set fileencoding=utf-8
from django.core.management.base import BaseCommand
from django.db import transaction
#from optparse import make_option

from documents.lib.bibtex import UglyBibtex
from optparse import make_option
import os

#Für die


class Command(BaseCommand):
    """ Dieses Commando erfordert einen Ordner 'olddb' im Projekt-Verzeichnis,
    welches Bibtex-Dateien enthält.
    """
    option_list = BaseCommand.option_list + (make_option('-b',
                                                         '--bibtex',
                                                         action='store_true',
                                                         dest='bibtex',
                                                         default=False,
                                                         help="Importiert nur die Bibtex-Dateien"),
                                             make_option('--basic-setup',
                                                         action='store_true',
                                                         dest='basic-setup',
                                                         default=False,
                                                         help="Erzeugt nur ein Setup mit den empfohlenen Einstellungen"),
                                             make_option('--make-demo',
                                                         action='store_true',
                                                         dest='demo',
                                                         default=False,
                                                         help=u"Erzeugt die Benutzer für eine Demo Umgebung"),
                                             make_option('--all',
                                                         action='store_true',
                                                         dest='all',
                                                         default=False,
                                                         help=u"""Erzeugt alles was für ein Demo-System benötigt wird bis
                                                         auf den Datenbank-Tabellen"""),
                                             )

    help = u"""Mit diesem Kommando kann folgendes erreicht werden:
        * Generierung eines default-Setups
        * Import von Ordnern mit BibTeX-Dateien
        * Erzeugung einer Demo-Instanz
        """
    args = "<bibtex_dir>"

    @transaction.commit_on_success
    def handle(self, *args, **options):
        print 'autocommit off'
        if options["basic-setup"] or options["all"]:
            print "Basic configuration"
            self.default_import_rules()
            self.default_settings()
            self.bibtex_categories()
        if options["demo"] or options["all"]:
            print "creating demo users"
            self.demo_users()
        if options["bibtex"] or options["all"]:
            print "BibTeX import"
            for file in os.listdir('olddb'):
                print 'handling', file
                if file.__str__().endswith('.bib'):
                    print 'importing', file
                    UglyBibtex('olddb/%s' % file).do_import()

    def default_import_rules(self):
        """ Erzeugt Importregeln für Dokumente.
        """
        from documents.models import Need
        from documents.models import NeedGroups
        # must have fields
        needed_field = ['author',
                        'title',
                        'publisher',
                        'year',
                        'school',
                        'note'
                        ]
        needed = {}
        ngroup = {}
        for field in needed_field:
            needed[field] = Need(name=field)
            needed[field].save()
        needed["author"] = Need(name="author")
        needed["author"].save()
        needed["editor"] = Need(name="editor")
        needed["editor"].save()

        for group in needed_field:
            ngroup[group] = NeedGroups(name=group)
            ngroup[group].save()
        ngroup["author_v_editor"] = NeedGroups(name="author_v_editor")
        ngroup["author_v_editor"].save()

        # Logical groups
        for group in NeedGroups.objects.all():
            if group.name == "author_v_editor":
                group.needs.add(needed["editor"])
                group.needs.add(needed["author"])
            else:
                group.needs.add(needed[group.name])
            group.save()

    def default_settings(self):
        """ Erzeugt empfohlene Einstellungen wie z.B. die Rechteverwaltung wie
        auch die Benutzergruppen
        """
        from django.contrib.auth.models import Group
        from django.contrib.auth.models import Permission
        from documents.models import Emails
        # creating groups
        self.g_admin = Group(name='Administrator')
        self.g_uadmin = Group(name='UserAdmin')
        self.g_biblio = Group(name='Bibliothekar')
        self.g_user = Group(name='Benutzer')
        self.g_admin.save()
        self.g_uadmin.save()
        self.g_biblio.save()
        self.g_user.save()
        # group permissions
            #useradmin
        Permission.objects.get(
                codename="add_group").group_set.add(self.g_uadmin)
        Permission.objects.get(
                codename="change_group").group_set.add(self.g_uadmin)
        Permission.objects.get(
                codename="delete_group").group_set.add(self.g_uadmin)
        Permission.objects.get(
                codename="add_user").group_set.add(self.g_uadmin)
        Permission.objects.get(
                codename="change_user").group_set.add(self.g_uadmin)
        Permission.objects.get(
                codename="delete_user").group_set.add(self.g_uadmin)
        Permission.objects.get(
                codename="can_see_last_update_info").group_set.add(self.g_uadmin)
        Permission.objects.get(
                codename="can_see_admin").group_set.add(self.g_uadmin)
        Permission.objects.get(
                codename="add_nonuser").group_set.add(self.g_uadmin)
        Permission.objects.get(
                codename="change_nonuser").group_set.add(self.g_uadmin)
        Permission.objects.get(
                codename="delete_nonuser").group_set.add(self.g_uadmin)
        Permission.objects.get(
                codename="add_emails").group_set.add(self.g_uadmin)
        Permission.objects.get(
                codename="change_emails").group_set.add(self.g_uadmin)
        Permission.objects.get(
                codename="can_send_mails").group_set.add(self.g_uadmin)
            #user
        Permission.objects.get(
                codename="can_see_price").group_set.add(self.g_user)
        Permission.objects.get(
                codename="can_see_locn").group_set.add(self.g_user)
        Permission.objects.get(
                codename="add_nonuser").group_set.add(self.g_user)
        Permission.objects.get(
                codename="change_nonuser").group_set.add(self.g_user)
        Permission.objects.get(
                codename="add_docstatus").group_set.add(self.g_user)
        Permission.objects.get(
                codename="change_docstatus").group_set.add(self.g_user)
        Permission.objects.get(
                codename="can_lend").group_set.add(self.g_user)
        Permission.objects.get(
                codename="can_unlend").group_set.add(self.g_user)
        Permission.objects.get(
                codename="can_miss").group_set.add(self.g_user)
            #Bibliothekar
        Permission.objects.get(
                codename="add_publisher").group_set.add(self.g_biblio)
        Permission.objects.get(
                codename="change_publisher").group_set.add(self.g_biblio)
        Permission.objects.get(
                codename="add_author").group_set.add(self.g_biblio)
        Permission.objects.get(
                codename="change_author").group_set.add(self.g_biblio)
        Permission.objects.get(
                codename="delete_author").group_set.add(self.g_biblio)
        Permission.objects.get(
                codename="add_document").group_set.add(self.g_biblio)
        Permission.objects.get(
                codename="change_document").group_set.add(self.g_biblio)
        Permission.objects.get(
                codename="can_see_price").group_set.add(self.g_biblio)
        Permission.objects.get(
                codename="can_see_locn").group_set.add(self.g_biblio)
        Permission.objects.get(
                codename="can_see_last_update_info").group_set.add(self.g_biblio)
        Permission.objects.get(
                codename="can_see_dop").group_set.add(self.g_biblio)
        Permission.objects.get(
                codename="can_see_export").group_set.add(self.g_biblio)
        Permission.objects.get(
                codename="add_documentauthors").group_set.add(self.g_biblio)
        Permission.objects.get(
                codename="change_documentauthors").group_set.add(self.g_biblio)
        Permission.objects.get(
                codename="delete_documentauthors").group_set.add(self.g_biblio)
        Permission.objects.get(
                codename="add_keywords").group_set.add(self.g_biblio)
        Permission.objects.get(
                codename="change_keywords").group_set.add(self.g_biblio)
        Permission.objects.get(
                codename="delete_keywords").group_set.add(self.g_biblio)
        Permission.objects.get(
                codename="add_docextra").group_set.add(self.g_biblio)
        Permission.objects.get(
                codename="change_docextra").group_set.add(self.g_biblio)
        Permission.objects.get(
                codename="delete_docextra").group_set.add(self.g_biblio)
        Permission.objects.get(
                codename="can_export").group_set.add(self.g_biblio)
        Permission.objects.get(
                codename="add_docstatus").group_set.add(self.g_biblio)
        Permission.objects.get(
                codename="change_docstatus").group_set.add(self.g_biblio)
        Permission.objects.get(
                codename="can_order").group_set.add(self.g_biblio)
        Permission.objects.get(
                codename="can_lost").group_set.add(self.g_biblio)
        Permission.objects.get(
                codename="add_emails").group_set.add(self.g_biblio)
        Permission.objects.get(
                codename="change_emails").group_set.add(self.g_biblio)
        Permission.objects.get(
                codename="can_send_mails").group_set.add(self.g_biblio)
            #Admin
        for perm in Permission.objects.all():
            perm.group_set.add(self.g_admin)
        #Emails
        e = Emails(name='Vermisst Gemeldet', subject='Vermisstmeldung',
                   text='Sehr geehrte Damen und Herren, \n\n Vor kurzem wurde' +
                        ' Dokument {{ document_name }} von {{ user_name }} als ' +
                        'vermisst gemeldet. \n Falls Sie 1. das Buch besitzen ' +
                        'sollten oder \n 2. Informationen über den Verbleib dieses' +
                        'Dokumentes haben, \n\n melden Sie dies bitte dem Institut ' +
                        'für Wissenschaftliches Rechnen. \n Für weitere ' +
                        'Informationen erkundigen Sie sich entweder bei dem ' +
                        '{{ user_name }} oder dem Institut. \n\n Diese E-Mail ' +
                        'wurde automatisch generiert und muss nicht beantwortet werden.')
        e.save()
        e = Emails(name='Frist Erinnerungsmail(B)', subject='Erinnerung_Bürge',
                   text='Sehr geehrter/e {{ user_name }}, \n\n ' +
                        'es wurde festgestellt, dass sich das Dokument {{ document_name }} noch in ' +
                        'dem Besitz eines Ihnen zugeteilten Externen befindet. \n' +
                        'Wir möchten Sie daran erinnern, dass die Rückgabefrist in wenigen Tagen ausläuft. \n\n ' +
                        'Bitte setzen Sie sich mit dem entsprechenden Externen ' +
                        'in Verbindung für eine Rückgabe oder eventuelle Verlängerung des Dokumentes. \n\n\n' +
                        'Institut: \n' +
                        'Institut für Wissenschaftliches Rechnen \n' +
                        'Technische Universität Braunschweig \n' +
                        'D-38092 Braunschweig \n' +
                        'Tel. +49-531-391-3000 \n' +
                        'Fax  +49-531-391-3003 \n' +
                        'Gebäude: Hans-Sommer-Straße 65 (Rechenzentrum) 1. Stock (PLZ 38106) \n\n\n' +
                        'Diese E-Mail wurde automatisch generiert und muss nicht beantwortet werden. ')
        e.save()
        e = Emails(name='Frist Erinnerungsmail(E)', subject='Erinnerung_Externer',
                   text='Sehr geehrter/e {{ nonuser_firstname }} {{ nonuser_lastname }} \n\n' +
                        'es wurde festgestellt, dass sich das Dokument {{ document_name }} noch in ihrem Besitz befindet. \n' +
                        'Wir möchten Sie daran erinnern, dass die Rückgabefrist in wenigen Tagen ausläuft. \n\n' +
                        'Bitte setzen Sie sich entweder mit dem Institut oder ihrem \n' +
                        'persönlichen Bürge in Verbindung für eine Rückgabe oder eventuelle Verlängerung \n' +
                        'des Dokumentes. \n\n\n' +
                        'Institut: \n' +
                        'Institut für Wissenschaftliches Rechnen \n' +
                        'Technische Universität Braunschweig \n' +
                        'D-38092 Braunschweig \n' +
                        'Tel. +49-531-391-3000 \n' +
                        'Fax  +49-531-391-3003 \n' +
                        'Gebäude: Hans-Sommer-Straße 65 (Rechenzentrum) 1. Stock (PLZ 38106) \n\n\n' +
                        'Diese E-Mail wurde automatisch generiert und muss nicht beantwortet werden.  ')
        e.save()

    def bibtex_categories(self):
        """ Erzeugt die meist genutzten BibTeX Kategorien die für eine
        Bibliothek benötigt werden.
        """
        from documents.models import Category
        from documents.models import NeedGroups
        need = {}
        for i in NeedGroups.objects.all():
            need[i.name] = i
        category = {"book": None,
                    "unpublished": None,
                    "projectwork": None,
                    "phdthesis": None,
                    "bachelorthesis": None,
                    "mastersthesis": None
                    }
        for c in category:
            category[c] = Category(name=c)
            category[c].save()
            category[c].needs.add(need["author_v_editor"],
                                  need["title"],
                                  )
        category["book"].needs.add(need["publisher"],
                                   need["year"]
                                   )
        category["book"].save()
        category["unpublished"].needs.add(need["note"])
        category["unpublished"].save()
        category["projectwork"].save()
        category["phdthesis"].needs.add(need["school"],
                                        need["year"]
                                        )
        category["phdthesis"].save()
        category["bachelorthesis"].needs.add(need["school"],
                                             need["year"],
                                             )
        category["bachelorthesis"].save()
        category["mastersthesis"].needs.add(need["school"],
                                            need["year"],
                                            need["author"]
                                            )
        category["mastersthesis"].save()

    def demo_users(self):
        from django.contrib.auth import get_user_model
        from django.contrib.auth.models import Group
        from django.contrib.auth.models import Permission
        #from django.conf import settings
        import datetime
        User = get_user_model()
        #User
        user1 = User(username="User1", first_name="Jörn", last_name="Hameyer",
                     email="user1@van-nahl.org",
                     is_staff=False, is_active=True, is_superuser=False,
                     last_login=datetime.datetime.today(),
                     date_joined=datetime.datetime.today()
                     )
        user1.set_password('sep2012')
        user1.save()
        user2 = User(username="User2", first_name="Stephan", last_name="Sobol",
                     email="user2@van-nahl.org", password=hash("sep2012"),
                     is_staff=False, is_active=True, is_superuser=False,
                     last_login=datetime.datetime.today(),
                     date_joined=datetime.datetime.today())
        user2.set_password("sep2012")
        user2.save()
        user3 = User(username="User3", first_name="Eric", last_name="Anders",
                     email="user3@van-nahl.org", password=hash("sep2012"),
                     is_staff=False, is_active=True, is_superuser=False,
                     last_login=datetime.datetime.today(),
                     date_joined=datetime.datetime.today())
        user3.set_password("sep2012")
        user3.save()
        user4 = User(username="User4", first_name="Johann", last_name="Hong",
                     email="user4@van-nahl.org", password=hash("sep2012"),
                     is_staff=False, is_active=True, is_superuser=False,
                     last_login=datetime.datetime.today(),
                     date_joined=datetime.datetime.today())
        user4.set_password("sep2012")
        user4.save()
        user5 = User(username="User5", first_name="Marco", last_name="Melzer",
                     email="user5@van-nahl.org", password=hash("sep2012"),
                     is_staff=False, is_active=True, is_superuser=False,
                     last_login=datetime.datetime.today(),
                     date_joined=datetime.datetime.today())
        user5.set_password("sep2012")
        user5.save()
        user6 = User(username="User6", first_name="Markus", last_name="Dietrich",
                     email="user6@van-nahl.org", password=hash("sep2012"),
                     is_staff=False, is_active=True, is_superuser=False,
                     last_login=datetime.datetime.today(),
                     date_joined=datetime.datetime.today())
        user6.set_password("sep2012")
        user6.save()
        user7 = User(username="User7", first_name="Philipp", last_name="Offensand",
                     email="user7@van-nahl.org", password=hash("sep2012"),
                     is_staff=False, is_active=True, is_superuser=False,
                     last_login=datetime.datetime.today(),
                     date_joined=datetime.datetime.today())
        user7.set_password("sep2012")
        user7.save()
        user8 = User(username="User8", first_name="Theodor van", last_name="Nahl",
                     email="user8@van-nahl.org", password=hash("sep2012"),
                     is_staff=False, is_active=True, is_superuser=False,
                     last_login=datetime.datetime.today(),
                     date_joined=datetime.datetime.today())
        user8.set_password("sep2012")
        user8.save()
        #adressen
        user1.street = "Musterstraße"
        user1.number = 1
        user1.zipcode = "12345"
        user1.city = "Musterhausen"
        user1.save()
        # user -> group
        groups = {}
        for i in Group.objects.all():
            groups[i.name] = i

        groups["Administrator"].user_set.add(user1)
        groups["Administrator"].user_set.add(user1)
        groups["Administrator"].user_set.add(user3)
        groups["Bibliothekar"].user_set.add(user1)
        groups["Bibliothekar"].user_set.add(user4)
        groups["Benutzer"].user_set.add(user1)
        groups["Benutzer"].user_set.add(user2)
        groups["Benutzer"].user_set.add(user3)
        groups["Benutzer"].user_set.add(user4)
        groups["Benutzer"].user_set.add(user5)
        groups["Benutzer"].user_set.add(user6)
        # ohne Gruppe user7(Rechte einfügen) und user8(ohne Rechte)
        #user7 Rechte geben
        Permission.objects.get(codename="can_see_price").user_set.add(user7)
        Permission.objects.get(codename="can_see_export").user_set.add(user7)
        Permission.objects.get(codename="can_lend").user_set.add(user7)
        Permission.objects.get(codename="can_unlend").user_set.add(user7)
        Permission.objects.get(codename="can_miss").user_set.add(user7)
        Permission.objects.get(codename="can_order").user_set.add(user7)
        Permission.objects.get(codename="can_lost").user_set.add(user7)
        Permission.objects.get(codename="can_see_history").user_set.add(user7)
        #user2 Rechte geben
        Permission.objects.get(codename="can_see_export").user_set.add(user2)
        Permission.objects.get(codename="can_export").user_set.add(user2)
