#!/usr/bin/env python
# vim set fileencoding=utf-8
import datetime
import re
from django.db import IntegrityError
from exceptions import UnknownCategoryError
from exceptions import DuplicateKeyError
from models import publisher
from models import category
from models import document
from models import author
from models import keywords
from models import doc_extra

def is_valid(dict_data): #TODO
    """Diese Methode überprüft, ob es sich bei dem übergebenen dict um ein 
    BibteX-kompatibles Format handelt"""
    try:
        bib_no_r = r"[PKDRM]\d+"#TODO regex im backend zur bearbeitung freigeben
        if not re.match(bib_no_r, dict_data["bib_no"]):
            return False, u"InformatikBibNo hat falsches Format"
        inv_no_r = r"\d{4}/\d+"
        if not re.match(inv_no_r, dict_data[u"inv_no"]):
            return False, u"Inventar-Nummer hat falsches Format"
        # Überprüfung auf Vollständigkeit für entsprechende Kategorien
        if dict_data[u"category"] == u"book": #checking book
            auths = dict_data.get(u"author", [])
            editors = dict_data.get(u"editor", [])
            if __lst_is_empty(auths) and __lst_is_empty(editors):
                return False, u"Autor und Editor"
            if dict_data[u"title"] == u"":
                return False, u"Title"
            if dict_data[u"publisher"] == u"":
                return False, u"Publisher"
            if dict_data[u"year"] == u"":
                return False, u"Year"
        elif dict_data[u"category"] == u"artictle": #checking article
            if __lst_is_empty(dict_data[u"author"]):
                return False, u"Autor"
            if dict_data[u"title"] == u"":
                return False, u"Title"
            if dict_data[u"journal"] == u"":
                return False, u"Journal"
            if dict_data[u"year"] == u"":
                return False, u"Year"
        elif dict_data[u"category"] == u"booklet": #checking booklet
            if dict_data[u"title"] == u"":
                return False, u"Title"
        elif dict_data[u"category"] == u"conference": #checking conference
            if __lst_is_empty(dict_data[u"author"]):
                return False, u"Autor"
            if dict_data[u"title"] == u"":
                return False, u"Title"
            if dict_data[u"booktitle"] == u"":
                return False, u"Booktitle"
            if dict_data[u"year"] == u"":
                return False, u"Year"
        elif dict_data[u"category"] == u"inbook": #checking inbook
            auths = dict_data.get(u"author", [])
            editors = dict_data.get(u"editor", [])
            if __lst_is_empty(auths + editors):
                return False, u"Autor und Editor"
            if dict_data[u"title"] == u"":
                return False, u"Title"
            if dict_data[u"booktitle"] == u"":
                return False, u"Booktitle"
            chapter = dict_data.get(u"chapter", u"")
            pages = dict_data.get(u"pages", u"")
            if (chapter + pages) == u"":
                return False, u"Chapter und Pages"
            if dict_data[u"publisher"] == u"":
                return False, u"Publisher"
            if dict_data[u"year"] == u"":
                return False, u"Year"
        elif dict_data[u"category"] == u"incollection": #checking incollection
            if __lst_is_empty(dict_data.get(u"author", [])):
                return False, u"Autor"
            if dict_data[u"title"] == u"":
                return False, u"Title"
            if dict_data[u"booktitle"] == u"":
                return False, u"Booktitle"
            if dict_data[u"publisher"] == u"":
                return False, u"Publisher"
            if dict_data[u"year"] == u"":
                return False, u"Year"
        elif dict_data[u"category"] == u"inproceedings": #checking inproceedings
            if __lst_is_empty(dict_data.get(u"author", [])):
                return False, u"Autor"
            if dict_data[u"title"] == u"":
                return False, u"Title"
            if dict_data[u"booktitle"] == u"":
                return False, u"Booktitle"
            if dict_data[u"year"] == u"":
                return False, u"Year"
        elif dict_data[u"category"] == u"manual": #checking manual
            if dict_data[u"address"] == u"":
                return False, u"Address"
            if dict_data["title"] == u"":
                return False, u"Title"
        elif dict_data[u"category"] == u"masterthesis": #checking masterthesis
            if __lst_is_empty(dict_data.get(u"author", [])):
                return False, u"Autor"
            if dict_data[u"title"] == u"":
                return False, u"Title"
            if dict_data[u"school"] == u"":
                return False, u"School"
            if dict_data[u"year"] == u"":
                return False, u"Year"
        elif dict_data[u"category"] == u"misc": #checking misc
            return True, u""
        elif dict_data[u"category"] == u"phdthesis": #checking phdthesis
            if __lst_is_empty(dict_data.get(u"author", [])):
                return False, u"Autor"
            if dict_data[u"title"] == u"":
                return False, u"Title"
            if dict_data[u"school"] == u"":
                return False, u"School"
            if dict_data[u"year"] == u"":
                return False, u"Year"
        elif dict_data[u"category"] == u"proceedings": #checking proceedings
            if dict_data[u"title"] == u"":
                return False, u"Title"
            if dict_data[u"year"] == u"":
                return False, u"Year"
        elif dict_data[u"category"] == u"techreport": #checking techreport
            if __lst_is_empty(dict_data.get(u"author", [])):
                return False, u"Autor"
            if dict_data[u"title"] == u"":
                return False, u"Title"
            if dict_data[u"institution"] == u"":
                return False, u"Institution"
            if dict_data[u"year"] == u"":
                return False, u"Year"
        elif dict_data[u"category"] == u"unpublished": #checking unpublished
            if __lst_is_empty(dict_data.get(u"author", [])):
                return False, u"Autor"
            if dict_data[u"title"] == u"":
                return False, u"Title"
            if dict_data[u"note"] == u"":
                return False, u"Note"
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
    try:
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
    try:
        # Erstellung des Dokumentes in der Datenbank, ebenso zugehörende
        # Elemente: author, publisher, editor, keywords...
        publisher_db, dummy = publisher.objects.get_or_create(name=publisher_f)
        try:
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
            au = auth.split(", ", 2)
            if len(au) > 1:
                last_name_f = au[0]
                first_name_f = au[1]
            else:
                name_f = au[0].split(" ")
                last_name_f = name_f[-1]
                first_name_f = " ".join(name_f[:-1])
            try:
                auth_db = author.objects.get(last_name=last_name_f, 
                        first_name=first_name_f)
            except author.DoesNotExist:
                auth_db = author(last_name=last_name_f,
                        first_name=first_name_f)
            auth_db.save()
            document_db.add_author(auth_db)
            document_db.save(user)

        for auth in editor_f:
            au = auth.split(", ", 2)
            if len(au) > 1:
                last_name_f = au[0]
                first_name_f = au[1]
            else:
                name_f = au[0].split(" ")
                last_name_f = name_f[-1]
                first_name_f = " ".join(name_f[:-1])
            try:
                auth_db = author.objects.get(last_name=last_name_f, 
                        first_name=first_name_f)
            except author.DoesNotExist:
                auth_db = author(last_name=last_name_f,
                        first_name=first_name_f)
            auth_db.save()
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
