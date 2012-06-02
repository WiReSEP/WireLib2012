#!/usr/bin/env python
# vim set fileencoding=utf-8
from datetime import datetime
import extras_doc_funcs
import re

class UglyBibtex(object):
    """ BibTeX-Parser zur Befüllung des Prototypen.
    Dieser BibTeX-Parser ist in der aktuellen Entwicklung nur zur Unterstützung
    der Prototyp-Entwicklung gedacht und sollte weiter nicht verwendet werden.
    """

    BIB_FIELDS = {
            u"informatikbibno" : u"bib_no",
            u"inventarno" : u"inv_no",
            # theoreticaly here: BibTeX-Id
            u"libraryofcongressno" : u"lib_of_con_nr",
            u"title" : u"title",
            u"isbn" : u"isbn",
            u"publisher" : u"publisher",
            u"year" : u"year",
            u"address" : u"address",
            u"price" : u"price",
            u"dateofpurchase" : u"date_of_purchase",
            u"author" : u"author",
            u"keywords" : u"keywords",
            }
    BIBTEX_SPLIT= r'[{}@,="\n]'

    def __init__(self, bibtex_file):
        self.bibtex_file = bibtex_file
        self.errout_file = bibtex_file+'.err'
        self.line = None
        self.line_no = 0
        self.worker = None                      # Aktuelle Arbeitsfunktion
        self.first_call = False
        self.stack = 0
        self.quotation_mark_stack = 0
        self.bracket_stack = 0
        self.entry = {}
        self.entrys = []

    def do_import(self):
        self.worker = self.do_import
        with open(self.bibtex_file,'r') as bib, open(self.errout_file) as errout:
            for self.line in bib:
                self.line_no += 1
                if re.match(r'^\s*@',self.line):
                    self.worker = self.__get_entry
                    self.first_call = True
                if self.worker != self.do_import:
                    try:
                        self.worker()
                    except ValueError:
                        print "Fehler im Datensatz!"
                        errout.write(self.line_no+" ")
                        errout.write("Fehler bei: "+self.line+'\n') # loglvl 1
                        errout.write("Bisher gelesen: "+self.entry+'\n') #lvl 2
                        errout.write('\n')
#                        Hier fehlt es noch, dass nach einem Erfolgreichen
#                        Abschluss die Daten in die DB eingetragen werden,
#                        exceptions abgefangen werden und die nötigen Variablen
#                        zurück gesetzt werden.

    def __get_entry(self):
        key_val = re.split(r'{', self.line)
        self.stack = 1
        self.stack -= self.line.count(r'}')
        if self.stack != 1:
            raise ValueError()
        self.entry_line = False
        if key_val != 2:
            raise ValueError()

        # Clean key_vals
        key_val[0] = re.sub(r'(^\s*@\s*)|(\s*$)','',key_val[0]).lower()
        key_val[1] = re.sub(r'(^\s*)|(\s*,\s*$)','',key_val[1])

        self.entry[UglyBibtex.BIB_FIELDS[key_val[0]]] = key_val[1]
        if self.line.count(',') == 1:
            self.worker = self.__get_field

    def __get_field(self):
        if self.line.count("=") > 1:
            raise ValueError()
        self.stack += self.line.count('{')
        self.stack -= self.line.count('}')
        self.quotation_mark_stack = self.line.count('"')
        self.bracket_stack += self.line.count("{")
        self.bracket_stack -= self.line.count("}")
        if self.stack == 0:
            self.worker = self.do_import
        if self.stack < 0:
            raise ValueError()
        key_val = self.line.split('=')
        if len(key_val) == 2:
            key_val[0].strip()
            re.sub(r'(^[\s"{]*)|(["}\s]*,\s*$)','',key_val[1])
## TODO: Wenn die stacks ok sagen, darf geschrieben werden und der
#            quotation_mark_stack wird zurückgesetzt. Wenn nicht, wird das
#            Bisherige gesichert und hoffentlich beim nächsten Durchlauf
#            mitgenommen... oder bei dem danach.
