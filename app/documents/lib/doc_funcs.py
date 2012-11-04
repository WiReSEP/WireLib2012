#!/usr/bin/env python
# vim set fileencoding=utf-8
import datetime
import re
from django.db import IntegrityError
from exceptions import UnknownCategoryError
from exceptions import DuplicateKeyError
from documents.models import Publisher
from documents.models import Category
from documents.models import Document
from documents.models import Author
from documents.models import Keywords
from documents.models import DocExtra

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
        cat = Category.objects.select_related().filter(pk=dict_data[u"category"])
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
        bib_no = dict_insert[u"bib_no"]
        inv_no = dict_insert[u"inv_no"]
        bibtex_id = dict_insert[u"bibtex_id"]
        lib_of_con_nr = dict_insert.get(u"lib_of_con_nr",None)
        title = dict_insert[u"title"]
        isbn = dict_insert.get(u"isbn", None)
        category = dict_insert[u"category"]
        publisher = dict_insert.get(u"publisher", None)
        year = dict_insert.get(u"year", None)
        address = dict_insert.get(u"address", None)
        price = dict_insert.get(u"price", None)
        currency = dict_insert.get(u"currency", None)
        date_of_purchase = dict_insert.get(u"date_of_purchase",
                datetime.date.today())
        ub_date = None
        comment = dict_insert.get(u"comment", None)
        authors = dict_insert.get(u"author",[])
        editors = dict_insert.get(u"editor",[])
        keywords = dict_insert.get(u"keywords", [])
        extra_fields = dict_insert.get(u"extras", {})
        last_updated = datetime.date.today()
        last_edit_by = user
    except KeyError:
        raise ValueError(u"Daten haben nicht die benötigten Felder")
    try :
        # Erstellung des Dokumentes in der Datenbank, ebenso zugehörende
        # Elemente: author, publisher, editor, keywords...
        publisher_db, dummy = Publisher.objects.get_or_create(name=publisher)
        try :
            category_db = Category.objects.get(name=category)
        except Category.DoesNotExist:
            raise UnknownCategoryError(category)
        document_db = Document(
                bib_no=bib_no, 
                inv_no=inv_no,
                bibtex_id=bibtex_id, 
                lib_of_con_nr=lib_of_con_nr,
                title=title, 
                isbn=isbn, 
                category=category_db, 
                publisher=publisher_db, 
                year=year, 
                address=address,
                price=price, 
                currency=currency,
                date_of_purchase=date_of_purchase, 
                ub_date=ub_date,
                comment=comment,
                last_updated= last_updated,
                last_edit_by = last_edit_by,
                )
        document_db.save(user)
        document_db.set_status(user, Document.AVAILABLE)
        for author in authors:
            author_db = _extract_author(author)
            document_db.add_author(author_db)
            document_db.save(user)

        for editor in editors:
            editor_db = _extract_author(auth)
            document_db.add_editor(editor_db)
            document_db.save(user)
        keywords_db = []

        for key in keywords:
            if key == '' or key == None:
                continue
            key_db, dummy = Keywords.objects.get_or_create(
                    document=document_db,
                    keyword=key)
            if dummy:
                keywords_db.append(key_db)
        extras_db = []
        for extra in extra_fields:
            value = extra_fields[extra]
            if value != "":
                extra_db, dummy = DocExtra.objects.get_or_create(
                    doc_id=document_db, bib_field=extra, content=value)
                if dummy:
                    extras_db.append(extra_db)
    except IntegrityError, e:
        print 'IntegrityError:', e
        raise DuplicateKeyError(e.message) #TODO regex basteln für Feld

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

def _extract_author(author):
    au = author.split(", ", 2)
    if len(au) > 1:
        last_name = au[0]
        first_name = au[1]
    else :
        name = au[0].split(" ")
        last_name = name[-1]
        first_name = " ".join(name[:-1])
    try :
        auth_db = Author.objects.get(last_name=last_name, 
            first_name=first_name)
    except Author.DoesNotExist:
        auth_db = Author(last_name=last_name,
            first_name=first_name)
    auth_db.save()
    return auth_db
