#!/usr/bin/env python
# vim set fileencoding=utf-8
import datetime
import re
from django.db import IntegrityError
from exceptions import UnknownCategoryError
from exceptions import DuplicateKeyError
from documents.models import publisher
from documents.models import category
from documents.models import document
from documents.models import author
from documents.models import keywords
from documents.models import doc_extra

def is_valid(dict_data): #TODO
    """Diese Methode überprüft, ob es sich bei dem übergebenen dict um ein 
    BibteX-kompatibles Format handelt"""
    try :
        bib_no_r = r"[PKDRM]\d+"#TODO regex im backend zur bearbeitung freigeben
        if not re.match(bib_no_r, dict_data["bib_no"]):
            return False, u"InformatikBibNo hat falsches Format"
        inv_no_r = r"\d{4}/\d+"
        if not re.match(inv_no_r, dict_data[u"inv_no"]):
            return False, u"Inventar-Nummer hat falsches Format"
        # Überprüfung auf Vollständigkeit für entsprechende Kategorien
        cat = category.objects.select_related().filter(pk=dict_data[u"category"])
        if len(cat) == 1:
            for group in cat[0].needs.all():
                group_satisfied = False
                for need in group.needs.all():
                    if not _var_is_empty(dict_data.get(need.name, [])):
                        group_satisfied = True
                if not group_satisfied:
                    return False, group.name
    except KeyError, e:
        return False, e.message
    return True, u""

def insert_doc(dict_insert, user):
    """Fügt ein Dokument aus einem dict in die Datenbank ein, nachdem es auf
    Validität überprüft wurde.
    """
    valid, message = is_valid(dict_insert)
    if not valid:
        pattern_und = r"\S* und \S*"
        pattern_complete = r".* hat falsches Format"
        if re.match(pattern_und, message):
            message = u"Die Felder " + message + u" sind leer"
        elif re.match(pattern_complete, message):
            pass
        else :
            message = u"Das Feld " + message + u" ist leer"
        raise ValueError(message)
    # .get wird verwendet für erlaubt fehlende Einträge
    try :
        bib_no_f = dict_insert[u"bib_no"]
        inv_no_f = dict_insert[u"inv_no"]
        bibtex_id_f = dict_insert[u"bibtex_id"]
        lib_of_con_nr_f = dict_insert.get(u"lib_of_con_nr",None)
        title_f = dict_insert[u"title"]
        isbn_f = dict_insert.get(u"isbn", None)
        category_f = dict_insert[u"category"]
        publisher_f = dict_insert.get(u"publisher", None)
        year_f = dict_insert.get(u"year", None)
        address_f = dict_insert.get(u"address", None)
        price_f = dict_insert.get(u"price", None)
        currency_f = dict_insert.get(u"currency", None)
        date_of_purchase_f = dict_insert.get(u"date_of_purchase",
                datetime.date.today())
        ub_date_f = None
        comment_f = dict_insert.get(u"comment", None)
        author_f = dict_insert.get(u"author",[])
        editor_f = dict_insert.get(u"editor",[])
        keywords_f = dict_insert.get(u"keywords", [])
        extra_fields_f = dict_insert.get(u"extras", {})
        last_updated_f = datetime.date.today()
        last_edit_by_f = user
    except KeyError:
        raise ValueError(u"Daten haben nicht die benötigten Felder")
    try :
        # Erstellung des Dokumentes in der Datenbank, ebenso zugehörende
        # Elemente: author, publisher, editor, keywords...
        publisher_db, dummy = publisher.objects.get_or_create(name=publisher_f)
        try :
            category_db = category.objects.get(name=category_f)
        except category.DoesNotExist:
            raise UnknownCategoryError(category_f)
        document_db = document(
                bib_no=bib_no_f, 
                inv_no=inv_no_f,
                bibtex_id=bibtex_id_f, 
                lib_of_con_nr=lib_of_con_nr_f,
                title=title_f, 
                isbn=isbn_f, 
                category=category_db, 
                publisher=publisher_db, 
                year=year_f, 
                address=address_f,
                price=price_f, 
                currency=currency_f,
                date_of_purchase=date_of_purchase_f, 
                ub_date=ub_date_f,
                comment=comment_f,
                last_updated= last_updated_f,
                last_edit_by = last_edit_by_f,
                )
        document_db.save(user)
        document_db.set_status(user, document.AVAILABLE)
        for auth in author_f:
            auth_db = _extract_author(auth)
            document_db.add_author(auth_db)
            document_db.save(user)

        for auth in editor_f:
            auth_db = _extract_author(auth)
            document_db.add_editor(auth_db)
            document_db.save(user)
        keywords_db = []

        for key in keywords_f:
            if key == '' or key == None:
                continue
            key_db, dummy = keywords.objects.get_or_create(
                    document=document_db,
                    keyword=key)
            if dummy:
                keywords_db.append(key_db)
        extras_db = []
        for extra in extra_fields_f:
            value = extra_fields_f[extra]
            if value != "":
                extra_db, dummy = doc_extra.objects.get_or_create(
                    doc_id=document_db, bib_field=extra, content=value)
                if dummy:
                    extras_db.append(extra_db)
    except IntegrityError, e:
        print 'IntegrityError:', e
        raise DuplicateKeyError(e.message) #TODO regex basteln für Feld

def __lst_is_empty(list_data):
    """
    Überprüfung einer Liste ob sie entweder keine ELemente enthält oder alle
    Elemente dem leeren String entsprechen.
    """
    if len(list_data) == 0:
        return True
    for i in list_data:
        if i == "":
            return True
    return False

def _var_is_empty(data):
    """
    Überprüfung einer Variablen auf Inhalt. True, falls 
        - None
        - leerer String
        - leere Liste
        - Liste mit leeren Strings.
    False sonst.
    """
    if data is None:
        return True
    elif type(data) == type("") or type(data) == type(u""):
        if len(data) == 0:
            return True
    elif type(data) == type([]):
        if len(data) == 0:
            return True
        for i in data:
            if len(i) > 0:
                return False
        return True
    else : 
        return False

def _extract_author(auth):
    au = auth.split(", ", 2)
    if len(au) > 1:
        last_name_f = au[0]
        first_name_f = au[1]
    else :
        name_f = au[0].split(" ")
        last_name_f = name_f[-1]
        first_name_f = " ".join(name_f[:-1])
    try :
        auth_db = author.objects.get(last_name=last_name_f, 
            first_name=first_name_f)
    except author.DoesNotExist:
        auth_db = author(last_name=last_name_f,
            first_name=first_name_f)
    auth_db.save()
    return auth_db
