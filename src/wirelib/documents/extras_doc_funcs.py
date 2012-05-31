from decimal import Decimal
import datetime
from models import publisher
from models import category
from models import document
from models import author
from models import keywords
from models import doc_extra

def insert_doc(dict_insert):
    bib_no_f = dict_insert[u"bib_no"]
    inv_no_f = dict_insert[u"inv_no"]
    bibtex_id_f = dict_insert[u"bibtex_id"]
    lib_of_con_nr_f = dict_insert[u"lib_of_con_nr"]
    title_f = dict_insert[u"title"]
    isbn_f = dict_insert.get(u"isbn", None)
    category_f = dict_insert[u"category"]
    status_f = dict_insert.get(u"status", 0)
    publisher_f = dict_insert[u"publisher"]
    year_f = dict_insert[u"year"]
    address_f = dict_insert.get(u"address", None)
    price_f = dict_insert.get(u"price", Decimal("0.00"))
    currency_f = dict_insert.get(u"currency", u"Eur")
    date_of_purchase_f = dict_insert.get(u"date_of_purchase",
            datetime.date.today())
    ub_date_f = None
    comment_f = dict_insert.get(u"comment", None)
    author_f = dict_insert[u"author"]
    keywords_f = dict_insert.get(u"keywords", [])
    extra_fields_f = dict_insert.get(u"extras", {})
    publisher_db, dummy = publisher.objects.get_or_create(name=publisher_f)
    category_db = category.objects.get(name=category_f)
    document_db = document(bib_no=bib_no_f, inv_no=inv_no_f,
            bibtex_id=bibtex_id_f, lib_of_con_nr=lib_of_con_nr_f,
            title=title_f, isbn=isbn_f, category=category_db, status=status_f,
            publisher=publisher_db, year=year_f, address=address_f,
            price=price_f, currency=currency_f,
            date_of_purchase=date_of_purchase_f, ub_date=ub_date_f,
            comment=comment_f)
    authors_db = []
    for auth in author_f:
        au = auth.split(u", ", maxsplit=2)
        if len(au) > 1:
            last_name_f = au[0]
            first_name_f = au[1]
        else:
            name_f = au[0].split(u" ")
            last_name_f = name_f[-1]
            first_name_f = u" ".join(name_f[:-2])
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
