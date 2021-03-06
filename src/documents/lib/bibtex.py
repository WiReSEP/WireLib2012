#!/usr/bin/env python
# vim set fileencoding=utf-8
from __future__ import unicode_literals
from django.conf import settings
from django.contrib.auth import get_user_model
from .exceptions import DuplicateKeyError
from .exceptions import UnknownCategoryError

import codecs
import datetime
import re
import threading


class UglyBibtex(object):

    """ BibTeX-Parser zur Befüllung des Prototypen.
    Dieser BibTeX-Parser ist in der aktuellen Entwicklung nur zur Unterstützung
    der Prototyp-Entwicklung gedacht und sollte weiter nicht verwendet werden.
    """

    BIB_FIELDS = {u"informatikbibno": u"bib_no",
                  u"inventarno": u"inv_no",
                  # theoreticaly here: BibTeX-Id
                  u"libraryofcongressno": u"lib_of_con_nr",
                  u"title": u"title",
                  u"isbn": u"isbn",
                  u"publisher": u"publisher",
                  u"year": u"year",
                  u"address": u"address",
                  u"dateofpurchase": u"date_of_purchase",
                  u"author": u"author",
                  u"editor": u"editor",
                  u"keywords": u"keywords",
                  }
    BIBTEX_SPLIT = r'[{}@,="\n]'

    def __init__(self, bibtex_file):
        self.bibtex_file = bibtex_file
        self.errout_file = bibtex_file + '.err'
        self.line = None
        self.line_no = 0
        self.worker = None                      # Aktuelle Arbeitsfunktion
        self.go_further = False
        self.stack = 0
        self.entry_txt = ''

        self.quotation_mark_stack = 0
        self.bracket_stack = 0
        self.current_keyval = []

        self.entry = {}
        self.extra_entry = {}

    def do_import(self):
        """ Importiert eine BibTeX-Datei in die Datenbank.
        Wichtig ist, dass die BibTeX-Datei dem WiRe-TU-BS-Format entspricht, da
        von dieser Funktion einige BibTeX-Fehler ignoriert werden und einige
        nicht valide Formate dennoch geparsed werden.

        Ein fehlerhafter Datensatz wird in eine extra-Datei gespeichert, direkt
        neben der Ursprungsdatei.
        """
        self.worker = self.do_import
        with codecs.open(self.bibtex_file, mode='r', encoding='utf-8') as bib:
            with codecs.open(self.errout_file, mode='w', encoding='utf-8') as self.errout:
                for self.line in bib:
                    self.entry_txt += self.line
                    self.line_no += 1
                    if re.match(r'^\s*@', self.line):
                        # Neuer Eintrag
                        self.worker = self.__get_entry

                    if self.worker != self.do_import:
                        # Eintrag abarbeiten.
                        try:
                            self.worker()
                        except ValueError as e:
                            if self.worker == self.__get_entry:
                                self.errout.write("#Eintrag hat einen Fehler: %s\n" % str(e).strip())
                            else:
                                self.errout.write("#Eintrag hat einen Fehler im Feld %s\n#%s\n" % (self.line.strip(), str(e).strip()))
                            self.__log_error()
                            self.worker = self.do_import
                    else:
                        # Eintragende, reset
                        self.go_further = False
                        self.stack = 0

                        self.quotation_mark_stack = 0
                        self.bracket_stack = 0
                        self.current_keyval = []
                        self.entry_txt = ""

                        self.entry = {}
                        self.extra_entry = {}

    def __get_entry(self):
        """ Nimmt einen Eintrag auf.
        Es wird direkt der Kopf eines Eintrages gespeichert und das Sammeln der
        einzelnen Einträge angestoßen.
        """
        key_val = re.split(r'{', self.line)
        self.stack = 1
        self.stack -= self.line.count(r'}')
        if self.stack != 1:
            raise ValueError('1')
        self.entry_line = False
        if len(key_val) != 2:
            raise ValueError('2')

        # Clean key_vals
        key_val[0] = re.sub(r'(^\s*@\s*)|(\s*$)', '', key_val[0]).lower()
        key_val[1] = re.sub(r'(^\s*)|(\s*,\s*$)', '', key_val[1])

        self.entry[u'category'] = key_val[0]
        self.entry[u'bibtex_id'] = key_val[1]
        head_end = re.match(r'.*,$', self.line.strip())
        if head_end:
            self.worker = self.__get_field
        else:
            raise ValueError('3')

    def __get_field(self):
        """ Nimmt das Feld eines Eintrages auf.
        Diese Methode übernimmt nur einen Eintrag eines Feldes und erkennt
        unstimmigkeiten sowohl in Feld als auch in Einträgen
        """
        from . import doc_funcs
        if self.line.count("=") > 1:
            raise ValueError('4')

        self.stack += self.line.count('{')
        self.stack -= self.line.count('}')
        if self.stack < 0:
            raise ValueError('5')
        elif self.stack == 0:   # Nach aktueller Zeile neuen Eintrag suchen
            self.worker = self.do_import

        self.quotation_mark_stack += self.line.count('"')
        self.bracket_stack += self.line.count("{")
        self.bracket_stack -= self.line.count("}")

        if self.bracket_stack > 0 or self.quotation_mark_stack % 2 == 1:
            self.go_further = True
        else:
            self.go_further = False
            self.bracket_stack = 0
            self.quotation_mark_stack = 0
        if self.worker == self.do_import and self.go_further:
            raise ValueError('6')  # Syntaxfehler

        key_val = self.line.split('=')
        if len(key_val) == 2:   # Einfacher Key = Value
            key_val[0] = key_val[0].lower().strip()
            key_val[1] = re.sub(
                r'(^[\s"{]*)|(["}\s]*(,|})\s*\n)', '', key_val[1])
            field_end = re.match('.*,$', self.line.strip())
            if (field_end and not self.go_further)  \
                    or self.worker == self.do_import:
                try:
                    self.__insert_field(key_val)
                except ValueError:
                    raise
            else:
                self.current_keyval = key_val
        elif len(key_val) == 1 and self.current_keyval:  # Nur noch Value Ergänzung
            key_val[0] = re.sub(r'(^\s*)|(["}\s]*,\s*$)', '', key_val[0])
            key_val.insert(0, self.current_keyval[0])
            key_val[1] = self.current_keyval[1].strip() + " " \
                + key_val[1].strip()
            field_end = re.match('.*,\s*$', self.line.strip())
            if field_end and not self.go_further:
                try:
                    self.__insert_field(key_val)
                except ValueError:
                    raise
                self.current_keyval = []
            if not field_end and not self.go_further:
                raise ValueError('7')
            else:
                self.current_keyval = key_val
        else:
            self.__log_error()
            raise ValueError('8')

        if self.worker == self.do_import:   # Eintrag in DB schreiben
            self.entry[u'extras'] = self.extra_entry
            try:
                doc_funcs.insert_doc(self.entry, get_user_model().objects.get(id=1))
                if getattr(settings, "BIBTEX_DEBUG", False):

                    self.__log_error()
            except ValueError as e:
                self.errout.write(u"#Eintrag kein valides Format. Grund: %s\n" % e.message)
                self.__log_error()
            except UnknownCategoryError:
                errmsg = "#Eintrag kein valides Format. Grund: Kategorie %s nicht bekannt\n" % self.entry[u'category']
                self.errout.write(errmsg)
                self.__log_error()
            except DuplicateKeyError as e:
                self.errout.write("#Eintrag bereits in der Datenbank vorhanden\n")
                self.__log_error()
            except Warning as e:
                self.errout.write("#Eintrag hat unbekannten mysql-Fehler erzeugt. %s" % e)
                self.__log_error()

    def __insert_field(self, key_val):
        if key_val[0] == u'author' or key_val[0] == u'editor':
            key_val[1] = key_val[1].split(',')
            key_val[0] = UglyBibtex.BIB_FIELDS[key_val[0]]
            key_val[1] = [s.strip() for s in key_val[1]]
            self.entry[key_val[0]] = key_val[1]

        elif key_val[0] == u'keywords':
            key_val[1] = re.split('[,;/]', key_val[1])
            key_val[0] = UglyBibtex.BIB_FIELDS[key_val[0]]
            key_val[1] = [s.strip() for s in key_val[1]]
            self.entry[key_val[0]] = key_val[1]

        elif key_val[0] == u'price':
            currency = {
                "€": "Euro",
                "$": "Dollar",
                "euro": "Euro",
                "DM": "DM",
                "Pounds": "Pfund",
            }
            # regex für währungen:
            value = key_val[1].strip().split(" ")
            current_currency = re.findall(r'[^0-9.\, ]*', key_val[1])
            # catch first match
            for i in current_currency:
                if i != '':
                    current_currency = i
                    break
            else:
                current_currency = None
            # replace unified short forms
            if current_currency in currency:
                current_currency = currency[current_currency]
            price = re.findall(r'''(\d* # price begin
                    [,|\.]?  # seperator
                    \d?\d?)? # last optional digits''',
                               key_val[1],
                               re.X)
            for i in price:
                if i != '':
                    price = i.replace(",", ".")
                    break
            else:
                price = None
            self.entry['price'] = price
            self.entry['currency'] = current_currency

        elif key_val[0] == u'dateofpurchase':
            if len(key_val) > 2:
                raise ValueError('9')
            try:
                mydatetime = datetime.datetime.strptime(
                    key_val[1], '%d.%m.%Y')
            except ValueError:
                return           # Mal wieder das falsche Format
            key_val[0] = UglyBibtex.BIB_FIELDS[key_val[0]]
            self.entry[key_val[0]] = mydatetime.date()

        elif key_val[0] in UglyBibtex.BIB_FIELDS:
            key_val[0] = UglyBibtex.BIB_FIELDS[key_val[0]]
            self.entry[key_val[0]] = key_val[1].strip()
        else:       # Extra Field
            self.extra_entry[key_val[0]] = key_val[1].strip()

    def __log_error(self):
        self.errout.write('#Fehler: Konnte folgenden Eintrag nicht übernehmen.\n')
        self.errout.write(self.entry_txt)
        self.errout.write('\n')


class Bibtex(threading.Thread):

    """ Threadfähiger Bibtex-Parser für den Import von Bibtex-Dateien in die
    Datenbank und für einen Export. Export sollte aus Sicherheitsgründen immer
    über einen Thread laufen, vorher muss jedoch die Funktion export_data()
    ausgeführt werden.
    """

    bibtex_lock = threading.Lock()
    """ Stellt sicher, dass nur ein Bibtex-Thread läuft. """
    docs_exported = 0
    docs_to_export = 0

    @staticmethod
    def get_state():
        if Bibtex.docs_to_export:
            return (Bibtex.docs_exported / Bibtex.docs_to_export)
        return 0

    def export_data(self, documents, export_path):
        """ Zum setzen der für den Export notwendigen Daten.
        """
        self.documents = documents
        Bibtex.docs_to_export = documents.count()
        self.export_path = export_path
        return self

    def run(self):
        if Bibtex.bibtex_lock.locked():
            return
        if not (self.documents and self.export_path):
            return
        Bibtex.bibtex_lock.acquire()
        self.__export_docs(self.documents, self.export_path)
        Bibtex.bibtex_lock.release()

    def do_import(self, file):
        """Diese Methode importiert die Dokumente einer Bibtex-Datei.
        """
        UglyBibtex(file).do_import()

    # def lex(input_str):
        #""" Die Analyse der Lexik
        #"""
        # self.tokens = (
            #'ENTRY_BEGIN',
            #'ENTRY_TYPE',
            #'ID',
            #'FIELD_NAME', 'EQUALS', 'FIELD_CONTENT', 'COMMA',
            #'LPARENT', 'RPARENT', 'QUOTATION_MARK',
        #)

        #   Tokens
        # t_ENTRY_BEGIN = r'@'
        # t_ENTRY_TYPE = r'[aAbBcCiImMpPtTuU]\w*'
        # t_ID = r'\w*'
        # t_FIELD_NAME = r'\w*'
        # t_EQUALS = r'='

        # t_FIELD_CONTENT = r'(\{(.|\n)*\} | "(.|\n)*" )'

        # t_COMMA = r','
        # t_LPARENT = r'\{'
        # t_RPARENT = r'\}'
        # t_QUOTATION_MARK = r'"'

        # Ignored characters
        # t_ignore = " \t"

        # def t_error(t):
            # raise TypeError("Invalid Format in %s" % (t.value))

        # Build the lexer
        # from . import ply.lex as lex
        # lex.lex()

        # lex.input(input_str)
        # for tok in iter(lex.token, None):
            # print repr(token.value), repr(token.type)

    @staticmethod
    def export_doc(document):
        """Diese Methode wandelt ein Dokument in einen BibTeX-kompatiblen
        String um.
        """
         # init der Variablen
        extra_fields = list(document.docextra_set.all())
        authors = list(document.authors.filter(
            documentauthors__editor=False
        ).order_by("documentauthors__sort_value"))
        editors = list(document.authors.filter(
            documentauthors__editor=True
        ).order_by("documentauthors__sort_value"))
        category = document.category.name
        bib_no = document.bib_no
        inv_no = document.inv_no
        bib_id = document.bibtex_id
        locn = document.lib_of_con_nr
        title = document.title
        isbn = document.isbn
        publisher = unicode(document.publisher)
        year = document.year
        address = document.address
        datePurchase = document.date_of_purchase
        datePurchase = datePurchase.strftime(u"%d.%m.%Y")
        comment = document.comment
        keywords = list(document.keywords_set.all())

         # Beginn mit schreiben des Strings
        doc_str = u"@" + category + u"{" + bib_id + u",\n"
        counter = 0
        last_element = len(authors) - 1
        doc_str += u"  author = {"
        if -1 == last_element:
            doc_str += u"},\n"
        for auth in authors:
            doc_str += auth.last_name + u", " + auth.first_name
            if counter == last_element:
                doc_str += u"},\n"
            else:
                doc_str += u" AND "
            counter += 1
        last_element = len(editors) - 1
        doc_str += u"  editor = {"
        if -1 == last_element:
            doc_str += u"},\n"
        for edit in editors:
            doc_str += edit.last_name + u", " + edit.first_name
            if counter == last_element:
                doc_str += u"},\n"
            else:
                doc_str += u" AND "
            counter += 1
        doc_str += u"  title = {" + title + u"},\n"
        if publisher is not None:
            doc_str += u"  publisher = {" + publisher + u"},\n"
        if year is not None:
            doc_str += u"  year = {" + str(year) + u"},\n"
        if address is not None:
            doc_str += u"  address = {" + address + u"},\n"
        if isbn is not None:
            doc_str += u"  isbn = {" + isbn + u"},\n"
        doc_str += u"  dateofpurchase = {" + datePurchase + u"},\n"
        doc_str += u"  inventarno = {" + inv_no + u"},\n"
        doc_str += u"  informatikbibno = {" + bib_no + u"},\n"
        if locn is not None:
            doc_str += u"  libraryofcongressno = {" + locn + u"},\n"
        doc_str += u"  keywords = {"
        counter = 0
        last_element = len(keywords) - 1
        if -1 == last_element:
            doc_str += u"},\n"
        for key in keywords:
            doc_str += key.keyword
            if counter == last_element:
                doc_str += u"},\n"
            else:
                doc_str += u" AND "
            counter += 1
        if comment is not None:
            doc_str += u"  comment = {" + comment + u"},\n"
        for extra in extra_fields:
            doc_str += u"  " + extra.bib_field + u" = {"
            doc_str += extra.content + u"},\n"
        doc_str += u"}"
        return doc_str

    active = False

    def __export_docs(self, documents, export_path):
        """ Viele Dokumente werden in eine Datei exportiert.
        """
        lock = threading.Lock()
        lock.acquire()
        if Bibtex.active is True:
            return
        lock.release()

        for doc in documents:
            doc_year = doc.date_of_purchase.year
            bib_filename = export_path + "/lib_%i_%s.bib" % (
                doc_year,
                datetime.date.today()
            )
            with codecs.open(bib_filename, mode='a', encoding='utf-8') \
                    as bib_file:
                bib_file.write(Bibtex.export_doc(doc))
            Bibtex.docs_exported += 1
        documents.update(bib_date=datetime.date.today())

        Bibtex.docs_exported = 0
        Bibtex.docs_to_export = 0

        lock.acquire()
        Bibtex.active = False
        lock.release()


#
# PLY Code for parsing Bibtex-Files
# =================================
#


# class BibtexEntry(object):
#    def __init__(self, field, content):
#        self.field = field
#        self.content = content
#
#    def __rep__(self):
#        return "Entry: %s = %s" % (self.field, self.content)

# Die Produktionen
""" TODO Zu testen sind geschweifte Klammern im Content, um das Handling sicher
zu stellen. Weiter fehlen noch die Produktionen für die Concatenation mit # """
