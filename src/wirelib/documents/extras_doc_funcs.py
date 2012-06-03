#!/usr/bin/env python
# vim set fileencoding=utf-8
import datetime
import re
from exceptions import UnknownCategoryError
from models import publisher
from models import category
from models import document
from models import author
from models import keywords
from models import doc_extra

def insert_doc(dict_insert):
    """Fügt ein Dokument aus einem dict in die Datenbank ein, nachdem es auf
    Validität überprüft wurde.
    """
    try:
        bib_no_f = dict_insert[u"bib_no"]
        inv_no_f = dict_insert[u"inv_no"]
        bibtex_id_f = dict_insert[u"bibtex_id"]
        lib_of_con_nr_f = dict_insert.get(u"lib_of_con_nr",None)
        title_f = dict_insert[u"title"]
        isbn_f = dict_insert.get(u"isbn", None)
        category_f = dict_insert[u"category"]
        status_f = dict_insert.get(u"status", 0)
        publisher_f = dict_insert.get(u"publisher", None)
        year_f = dict_insert.get(u"year", None)
        address_f = dict_insert.get(u"address", None)
        price_f = dict_insert.get(u"price", None)
        currency_f = dict_insert.get(u"currency", None)
        date_of_purchase_f = dict_insert.get(u"date_of_purchase",
                datetime.date.today())
        ub_date_f = None
        comment_f = dict_insert.get(u"comment", None)
        author_f = dict_insert[u"author"]
        keywords_f = dict_insert.get(u"keywords", [])
        extra_fields_f = dict_insert.get(u"extras", {})
    except KeyError:
        raise ValueError(u"Data is not valid")
    if not is_valid(dict_insert):
        raise ValueError(u"Data is not valid")
    publisher_db, dummy = publisher.objects.get_or_create(name=publisher_f)
    try:
        category_db = category.objects.get(name=category_f)
    except category.DoesNotExist:
        raise UnknownCategoryError(category_f)
    document_db = document(bib_no=bib_no_f, inv_no=inv_no_f,
            bibtex_id=bibtex_id_f, lib_of_con_nr=lib_of_con_nr_f,
            title=title_f, isbn=isbn_f, category=category_db, status=status_f,
            publisher=publisher_db, year=year_f, address=address_f,
            price=price_f, currency=currency_f,
            date_of_purchase=date_of_purchase_f, ub_date=ub_date_f,
            comment=comment_f)
    authors_db = []
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
            # auth_db.documents.add(document_db)
        except author.DoesNotExist:
            auth_db = author(last_name=last_name_f,
                    first_name=first_name_f)
            # auth_db.documents.add(document_db)
        auth_db.save()
        authors_db.append(auth_db)
        document_db.authors.add(auth_db)
    keywords_db = []
    for key in keywords_f:
        key_db, dummy = keywords.objects.get_or_create(document=document_db,
                keyword=key)
        keywords_db.append(key_db)
    extras_db = []
    for extra in extra_fields_f:
        value = extra_fields_f[extra]
        extra_db, dummy = doc_extra.objects.get_or_create(
                doc_id=document_db, bib_field=extra, content=value)
        extras_db.append(extra_db)
    document_db.save()

def is_valid(dict_data): #TODO
    """Diese Methode überprüft, ob es sich bei dem übergebenen dict um ein 
    BibteX-kompatibles Format handelt"""
    try:
        bib_no_r = r"[PKDRM]\d+"
        if not re.match(bib_no_r, dict_data["bib_no"]):
            return False
        inv_no_r = r"\d{4}/\d{3}"
        if not re.match(inv_no_r, dict_data[u"inv_no"]):
            return False
        if dict_data[u"category"] == u"book": #checking book
            auths = dict_data.get(u"author", [])
            extras = dict_data.get(u"extras", {})
            editors = extras.get(u"editor", [])
#            print auths, editors, (auths + editors)
            if __lst_is_empty(auths + editors):
                return False
            if dict_data[u"title"] == u"":
                return False
            if dict_data[u"publisher"] == u"":
                return False
            if dict_data[u"year"] == u"":
                return False
        elif dict_data[u"category"] == u"artictle": #checking article
            if __lst_is_empty(dict_data[u"author"]):
                return False
            if dict_data[u"title"] == u"":
                return False
            if dict_data[u"journal"] == u"":
                return False
            if dict_data[u"year"] == u"":
                return False
        elif dict_data[u"category"] == u"booklet": #checking booklet
            if dict_data[u"title"] == u"":
                return False
        elif dict_data[u"category"] == u"conference": #checking conference
            if __lst_is_empty(dict_data[u"author"]):
                return False
            if dict_data[u"title"] == u"":
                return False
            if dict_data[u"booktitle"] == u"":
                return False
            if dict_data[u"year"] == u"":
                return False
        elif dict_data[u"category"] == u"inbook": #checking inbook
            auths = dict_data.get(u"author", [])
            extras = dict_data.get(u"extras", {})
            editors = extras.get(u"editor", [])
            if __lst_is_empty(auths.extend(editors)):
                return False
            if dict_data[u"title"] == u"":
                return False
            if dict_data[u"booktitle"] == u"":
                return False
            chapter = dict_data.get(u"chapter", u"")
            pages = dict_data.get(u"pages", u"")
            if (chapter + pages) == u"":
                return False
            if dict_data[u"publisher"] == u"":
                return False
            if dict_data[u"year"] == u"":
                return False
        elif dict_data[u"category"] == u"incollection": #checking incollection
            if __lst_is_empty(dict_data.get(u"author", [])):
                return False
            if dict_data[u"title"] == u"":
                return False
            if dict_data[u"booktitle"] == u"":
                return False
            if dict_data[u"publisher"] == u"":
                return False
            if dict_data[u"year"] == u"":
                return False
        elif dict_data[u"category"] == u"inproceedings": #checking inproceedings
            if __lst_is_empty(dict_data.get(u"author", [])):
                return False
            if dict_data[u"title"] == u"":
                return False
            if dict_data[u"booktitle"] == u"":
                return False
            if dict_data[u"year"] == u"":
                return False
        elif dict_data[u"category"] == u"manual": #checking manual
            if dict_data[u"address"] == u"":
                return False
            if dict_data["title"] == u"":
                return False
        elif dict_data[u"category"] == u"masterthesis": #checking masterthesis
            if __lst_is_empty(dict_data.get(u"author", [])):
                return False
            if dict_data[u"title"] == u"":
                return False
            if dict_data[u"school"] == u"":
                return False
            if dict_data[u"year"] == u"":
                return False
        elif dict_data[u"category"] == u"misc": #checking misc
            return True
        elif dict_data[u"category"] == u"phdthesis": #checking phdthesis
            if __lst_is_empty(dict_data.get(u"author", [])):
                return False
            if dict_data[u"title"] == u"":
                return False
            if dict_data[u"school"] == u"":
                return False
            if dict_data[u"year"] == u"":
                return False
        elif dict_data[u"category"] == u"proceedings": #checking proceedings
            if dict_data[u"title"] == u"":
                return False
            if dict_data[u"year"] == u"":
                return False
        elif dict_data[u"category"] == u"techreport": #checking techreport
            if __lst_is_empty(dict_data.get(u"author", [])):
                return False
            if dict_data[u"title"] == u"":
                return False
            if dict_data[u"institution"] == u"":
                return False
            if dict_data[u"year"] == u"":
                return False
        elif dict_data[u"category"] == u"unpublished": #checking unpublished
            if __lst_is_empty(dict_data.get(u"author", [])):
                return False
            if dict_data[u"title"] == u"":
                return False
            if dict_data[u"note"] == u"":
                return False
    except KeyError:
        return False
    return True

def __lst_is_empty(list_data):
    if len(list_data) == 0:
        return True
    for i in list_data:
        if i == "":
            return True
    return False
