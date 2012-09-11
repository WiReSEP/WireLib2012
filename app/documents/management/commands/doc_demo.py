#vim: set fileencoding=utf-8
from django.core.management.base import BaseCommand
#from optparse import make_option

from documents.extras_bibtex import UglyBibtex
import os

#Für die 

class Command(BaseCommand):
    help = "Hier kann der documents-App eine Demo-Session hinzugefügt werden"
    args = ""

    def handle(self, *args, **options):
        Command.__base_init()
        for file in os.listdir('olddb'):
            if file.__str__().endswith('.bib'):
                UglyBibtex('olddb/%s'%file).do_import()

    @staticmethod
    def __base_init():
        from django.contrib.auth.models import Group
        from django.contrib.auth.models import Permission
        from django.contrib.auth.models import User
        from documents.models import category
        from documents.models import emails
        from documents.models import need
        from documents.models import need_groups
        from documents.models import tel_user
        from documents.models import user_profile
        import datetime

        #Mussfeldergruppen(name)
        mg_au_ed = need_groups(name='author_v_editor')
        mg_title = need_groups(name='title')
        mg_publisher = need_groups(name='publisher')
        mg_year = need_groups(name='year')
        mg_author = need_groups(name='author')
        mg_school = need_groups(name='school')
        mg_note = need_groups(name='note')
        mg_au_ed.save()
        mg_title.save()
        mg_publisher.save()
        mg_year.save()
        mg_author.save()
        mg_school.save()
        mg_note.save()
        
        #Mussfelder(name, group)
        m = need(name='author', group=mg_au_ed)
        m.save()
        m = need(name='author', group=mg_author)
        m.save()
        m = need(name='editor', group=mg_au_ed)
        m.save()
        m = need(name='title', group=mg_title)
        m.save()
        m = need(name='publisher', group=mg_publisher)
        m.save()
        m = need(name='year', group=mg_year)
        m.save()
        m = need(name='school', group=mg_school)
        m.save()
        m = need(name='note', group=mg_note)
        m.save()
    
        #Kategorien
        c_book = category(name='book')
        c_book.save()
        c_book.needs.add(mg_au_ed)
        c_book.needs.add(mg_title)
        c_book.needs.add(mg_publisher)
        c_book.needs.add(mg_year)
        
        c_unpub = category(name='unpublished')
        c_unpub.save()
        c_unpub.needs.add(mg_author)
        c_unpub.needs.add(mg_title)
        c_unpub.needs.add(mg_note)
        
        c_proj = category(name='projectwork')
        c_proj.save()
        
        c_phdt = category(name='phdthesis')
        c_phdt.save()
        c_phdt.needs.add(mg_author)
        c_phdt.needs.add(mg_title)
        c_phdt.needs.add(mg_school)
        c_phdt.needs.add(mg_year)
        
        c_bach = category(name='bachelorthesis')
        c_bach.save()
        c_bach.needs.add(mg_author)
        c_bach.needs.add(mg_title)
        c_bach.needs.add(mg_school)
        c_bach.needs.add(mg_year)
        
        c_mast = category(name='mastersthesis')
        c_mast.save()
        c_mast.needs.add(mg_author)
        c_mast.needs.add(mg_title)
        c_mast.needs.add(mg_school)
        c_mast.needs.add(mg_year)
        
        #User
        user1 = User(username="User1", first_name="Jörn", last_name="Hameyer", 
                  email="user1@van-nahl.org", 
                  is_staff=False, is_active=True, is_superuser=False, 
                  last_login=datetime.datetime.today(), 
                  date_joined=datetime.datetime.today())
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
        a1 = user_profile(user_id=user1, street="Musterstraße", number="1",
                          zipcode="12345", city="Musterhausen")
        a1.save()
        a2 = user_profile(user_id=user2, street="Musterstraße", number="2",
                          zipcode="12345", city="Musterhausen")
        a2.save()
        a3 = user_profile(user_id=user3, street="Musterstraße", number="3",
                          zipcode="12345", city="Musterhausen")
        a3.save()
        a4 = user_profile(user_id=user4, street="Musterstraße", number="4",
                          zipcode="12345", city="Musterhausen")
        a4.save()
        a5 = user_profile(user_id=user5, street="Musterstraße", number="5",
                          zipcode="12345", city="Musterhausen")
        a5.save()
        a6 = user_profile(user_id=user6, street="Musterstraße", number="6",
                          zipcode="12345", city="Musterhausen")
        a6.save()
        a7 = user_profile(user_id=user7, street="Musterstraße", number="7",
                          zipcode="12345", city="Musterhausen")
        a7.save()
        a8 = user_profile(user_id=user8, street="Musterstraße", number="8",
                          zipcode="12345", city="Musterhausen")
        a8.save()
    
        #Gruppe + user->Gruppe
        g_admin = Group(name='Administrator')
        g_admin.save()
        g_admin.user_set.add(user1)
        g_uadmin = Group(name='UserAdmin')
        g_uadmin.save()
        g_uadmin.user_set.add(user1)
        g_uadmin.user_set.add(user3)
        g_biblio = Group(name='Bibliothekar')
        g_biblio.save()
        g_biblio.user_set.add(user1)
        g_biblio.user_set.add(user4)
        g_user = Group(name='Mitglieder')
        g_user.save()
        g_user.user_set.add(user1)
        g_user.user_set.add(user2)
        g_user.user_set.add(user3)
        g_user.user_set.add(user4)
        g_user.user_set.add(user5)
        g_user.user_set.add(user6)
        # ohne Gruppe user7(Rechte einfügen) und user8(ohne Rechte)            
    
        #user7 Rechte geben
        Permission.objects.get(codename="can_see_price").user_set.add(user7)
        Permission.objects.get(codename="can_see_export").user_set.add(user7)
        Permission.objects.get(codename="can_import").user_set.add(user7)
        Permission.objects.get(codename="can_lend").user_set.add(user7)
        Permission.objects.get(codename="can_unlend").user_set.add(user7)
        Permission.objects.get(codename="can_miss").user_set.add(user7)
        Permission.objects.get(codename="can_order").user_set.add(user7)
        Permission.objects.get(codename="can_lost").user_set.add(user7)
        Permission.objects.get(codename="can_see_history").user_set.add(user7)
        
        
        #user2 Rechte geben
        Permission.objects.get(codename="can_see_export").user_set.add(user2)
        Permission.objects.get(codename="can_export").user_set.add(user2)
        
        
        #group
            #useradmin
        Permission.objects.get(codename="add_group").group_set.add(g_uadmin)
        Permission.objects.get(codename="change_group").group_set.add(g_uadmin)
        Permission.objects.get(codename="delete_group").group_set.add(g_uadmin)
        Permission.objects.get(codename="add_user").group_set.add(g_uadmin)
        Permission.objects.get(codename="change_user").group_set.add(g_uadmin)
        Permission.objects.get(codename="delete_user").group_set.add(g_uadmin)
        Permission.objects.get(codename="can_see_last_update_info").group_set.add(g_uadmin)
        Permission.objects.get(codename="add_user_profile").group_set.add(g_uadmin)
        Permission.objects.get(codename="change_user_profile").group_set.add(g_uadmin)
        Permission.objects.get(codename="delete_user_profile").group_set.add(g_uadmin)
        Permission.objects.get(codename="can_see_admin").group_set.add(g_uadmin)
        Permission.objects.get(codename="can_see_others_groups").group_set.add(g_uadmin)
        Permission.objects.get(codename="add_tel_user").group_set.add(g_uadmin)
        Permission.objects.get(codename="change_tel_user").group_set.add(g_uadmin)
        Permission.objects.get(codename="delete_tel_user").group_set.add(g_uadmin)
        Permission.objects.get(codename="add_non_user").group_set.add(g_uadmin)
        Permission.objects.get(codename="change_non_user").group_set.add(g_uadmin)
        Permission.objects.get(codename="delete_non_user").group_set.add(g_uadmin)
        Permission.objects.get(codename="add_tel_non_user").group_set.add(g_uadmin)
        Permission.objects.get(codename="change_tel_non_user").group_set.add(g_uadmin)
        Permission.objects.get(codename="delete_tel_non_user").group_set.add(g_uadmin)
        Permission.objects.get(codename="add_emails").group_set.add(g_uadmin)
        Permission.objects.get(codename="change_emails").group_set.add(g_uadmin)
        Permission.objects.get(codename="can_send_mails").group_set.add(g_uadmin)
        
            #user
        Permission.objects.get(codename="can_see_price").group_set.add(g_user)
        Permission.objects.get(codename="can_see_locn").group_set.add(g_user)
        Permission.objects.get(codename="add_non_user").group_set.add(g_user)
        Permission.objects.get(codename="change_non_user").group_set.add(g_user)
        Permission.objects.get(codename="add_tel_non_user").group_set.add(g_user)
        Permission.objects.get(codename="change_tel_non_user").group_set.add(g_user)
        Permission.objects.get(codename="add_doc_status").group_set.add(g_user)
        Permission.objects.get(codename="change_doc_status").group_set.add(g_user)
        Permission.objects.get(codename="can_lend").group_set.add(g_user)
        Permission.objects.get(codename="can_unlend").group_set.add(g_user)
        Permission.objects.get(codename="can_miss").group_set.add(g_user)
        Permission.objects.get(codename="can_see_history").group_set.add(g_user)
        
            #Bibliothekar
        Permission.objects.get(codename="add_publisher").group_set.add(g_biblio)
        Permission.objects.get(codename="change_publisher").group_set.add(g_biblio)
        Permission.objects.get(codename="add_author").group_set.add(g_biblio)
        Permission.objects.get(codename="change_author").group_set.add(g_biblio)
        Permission.objects.get(codename="delete_author").group_set.add(g_biblio)
        Permission.objects.get(codename="add_document").group_set.add(g_biblio)
        Permission.objects.get(codename="change_document").group_set.add(g_biblio)
        Permission.objects.get(codename="can_see_price").group_set.add(g_biblio)
        Permission.objects.get(codename="can_see_locn").group_set.add(g_biblio)
        Permission.objects.get(codename="can_see_last_update_info").group_set.add(g_biblio)
        Permission.objects.get(codename="can_see_dop").group_set.add(g_biblio)
        Permission.objects.get(codename="can_see_export").group_set.add(g_biblio)
        Permission.objects.get(codename="add_document_authors").group_set.add(g_biblio)
        Permission.objects.get(codename="change_document_authors").group_set.add(g_biblio)
        Permission.objects.get(codename="delete_document_authors").group_set.add(g_biblio)
        Permission.objects.get(codename="add_keywords").group_set.add(g_biblio)
        Permission.objects.get(codename="change_keywords").group_set.add(g_biblio)
        Permission.objects.get(codename="delete_keywords").group_set.add(g_biblio)
        Permission.objects.get(codename="add_doc_extra").group_set.add(g_biblio)
        Permission.objects.get(codename="change_doc_extra").group_set.add(g_biblio)
        Permission.objects.get(codename="delete_doc_extra").group_set.add(g_biblio)
        Permission.objects.get(codename="can_import").group_set.add(g_biblio)
        Permission.objects.get(codename="can_export").group_set.add(g_biblio)
        Permission.objects.get(codename="add_doc_status").group_set.add(g_biblio)
        Permission.objects.get(codename="change_doc_status").group_set.add(g_biblio)
        Permission.objects.get(codename="can_order").group_set.add(g_biblio)
        Permission.objects.get(codename="can_lost").group_set.add(g_biblio)
        Permission.objects.get(codename="add_emails").group_set.add(g_biblio)
        Permission.objects.get(codename="change_emails").group_set.add(g_biblio)
        Permission.objects.get(codename="can_send_mails").group_set.add(g_biblio)
        
            #Admin
        for perm in Permission.objects.all():
            perm.group_set.add(g_admin)
        
        #Emails
        e = emails(name='Vermisst Gemeldet', subject='Vermisstmeldung', 
                   text='Sehr geehrte Damen und Herren, \n\n Vor kurzem wurde' + 
                        ' Dokument {{ document_name }} von {{ user_name }} als ' + 
                        'vermisst gemeldet. \n Falls Sie 1. das Buch besitzen ' + 
                        'sollten oder \n 2. Informationen über den Verbleib dieses' +  
                        'Dokumentes haben, \n\n melden Sie dies bitte dem Institut '+ 
                        'für Wissenschaftliches Rechnen. \n Für weitere ' +  
                        'Informationen erkundigen Sie sich entweder bei dem ' + 
                        '{{ user_name }} oder dem Institut. \n\n Diese E-Mail ' + 
                        'wurde automatisch generiert und muss nicht beantwortet werden.')
        e.save()
        e = emails(name='Frist Erinnerungsmail(B)', subject='Erinnerung_Bürge', 
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
        e = emails(name='Frist Erinnerungsmail(E)', subject='Erinnerung_Externer', 
                   text='Sehr geehrter/e {{ nonuser_firstname }} {{ nonuser_lastname }} \n\n'+
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
