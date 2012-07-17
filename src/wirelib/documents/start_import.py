#!/usr/bin/env python
# vim set fileencoding=utf-8
from documents.models import category
from documents.models import category_need
from documents.models import user_profile
from documents.models import tel_user
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.auth.models import User
import datetime

def importieren():
    #Kategorien
    c_book = category(name='book')
    c_book.save()
    c_unpub = category(name='unpublished')
    c_unpub.save()
    c_proj = category(name='projectwork')
    c_proj.save()
    c_phdt = category(name='phdthesis')
    c_phdt.save()
    c_bach = category(name='bachelorthesis')
    c_bach.save()
    c_mast = category(name='mastersthesis')
    c_mast.save()

    #Kategories-Need
        #book
    cn = category_need(category=c_book, need="author")
    cn.save()
    cn = category_need(category=c_book, need="editor")
    cn.save()
    cn = category_need(category=c_book, need="title")
    cn.save()    
    cn = category_need(category=c_book, need="publisher")
    cn.save()    
    cn = category_need(category=c_book, need="year")
    cn.save() 
        #unpublished
    cn = category_need(category=c_unpub, need="author")
    cn.save()
    cn = category_need(category=c_unpub, need="title")
    cn.save()
    cn = category_need(category=c_unpub, need="note")
    cn.save()
        #phdthesis
    cn = category_need(category=c_phdt, need="author")
    cn.save()
    cn = category_need(category=c_phdt, need="title")
    cn.save()
    cn = category_need(category=c_phdt, need="school")
    cn.save()
    cn = category_need(category=c_phdt, need="year")
    cn.save()
        #bachelorthesis
    cn = category_need(category=c_bach, need="author")
    cn.save()
    cn = category_need(category=c_bach, need="title")
    cn.save()
    cn = category_need(category=c_bach, need="school")
    cn.save()
    cn = category_need(category=c_bach, need="year")
    cn.save()
        #masterthesis
    cn = category_need(category=c_mast, need="author")
    cn.save()
    cn = category_need(category=c_mast, need="title")
    cn.save()
    cn = category_need(category=c_mast, need="school")
    cn.save()
    cn = category_need(category=c_mast, need="year")
    cn.save()
    
    #User
    user1 = User(username="User1", first_name="Jörn", last_name="Hameyer", 
              email="user1@van-nahl.org", password=hash("sep2012"), 
              is_staff=False, is_active=False, is_superuser=False, 
              last_login=datetime.datetime.today(), 
              date_joined=datetime.datetime.today())
    user1.set_password("sep2012")
    user1.save()
    user2 = User(username="User2", first_name="Stephan", last_name="Sobol", 
              email="user2@van-nahl.org", password=hash("sep2012"), 
              is_staff=False, is_active=False, is_superuser=False, 
              last_login=datetime.datetime.today(), 
              date_joined=datetime.datetime.today())
    user2.set_password("sep2012")
    user2.save()
    user3 = User(username="User3", first_name="Eric", last_name="Anders", 
              email="user3@van-nahl.org", password=hash("sep2012"), 
              is_staff=False, is_active=False, is_superuser=False,
              last_login=datetime.datetime.today(), 
              date_joined=datetime.datetime.today())
    user3.set_password("sep2012")
    user3.save()
    user4 = User(username="User4", first_name="Johann", last_name="Hong", 
              email="user4@van-nahl.org", password=hash("sep2012"), 
              is_staff=False, is_active=False, is_superuser=False,
              last_login=datetime.datetime.today(), 
              date_joined=datetime.datetime.today())
    user4.set_password("sep2012")
    user4.save()
    user5 = User(username="User5", first_name="Marco", last_name="Melzer", 
              email="user5@van-nahl.org", password=hash("sep2012"), 
              is_staff=False, is_active=False, is_superuser=False,
              last_login=datetime.datetime.today(), 
              date_joined=datetime.datetime.today())
    user5.set_password("sep2012")
    user5.save()
    user6 = User(username="User6", first_name="Markus", last_name="Dietrich", 
              email="user6@van-nahl.org", password=hash("sep2012"), 
              is_staff=False, is_active=False, is_superuser=False,
              last_login=datetime.datetime.today(), 
              date_joined=datetime.datetime.today())
    user6.set_password("sep2012")
    user6.save()
    user7 = User(username="User7", first_name="Philipp", last_name="Offensand", 
              email="user7@van-nahl.org", password=hash("sep2012"), 
              is_staff=False, is_active=False, is_superuser=False,
              last_login=datetime.datetime.today(), 
              date_joined=datetime.datetime.today())
    user7.set_password("sep2012")
    user7.save()
    user8 = User(username="User8", first_name="Theodor van", last_name="Nahl", 
              email="user8@van-nahl.org", password=hash("sep2012"),
              is_staff=False, is_active=False, is_superuser=False,
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
    
