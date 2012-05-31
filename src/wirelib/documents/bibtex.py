#!/usr/bin/env python
# vim set fileencoding=utf-8
from datetime import datetime
import extras_doc_funcs
import re

class bibtex(object):
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

    def __init__(self, file):
        self.file = file
        self.bib_file = None
        self.entry = {}

    def do_import(self):
        """ Diese Methode geht von einem sehr unflexiblen Format für
        BibTeX-Dateien aus. Sie ist also nicht robust!
        """
        self.bib_file = open(self.file,'r')
        for line in self.bib_file:
            if re.match(r'\s*@',line):
#                print "entering entry"
                self.__get_entry(line)
        self.bib_file.close()

    def __get_entry(self,line):
        """ Ist u.a. für die Mangelnde Robustheit der do_import()
        verantwortlich.
        """
        key_val = re.split(bibtex.BIBTEX_SPLIT, line)
        key_val = self.__clean_list(key_val)
        if len(key_val) != 2:
            raise  ValueError()
        self.entry[u'category'] = key_val[0].lower()
        self.entry[u'bibtex_id'] = key_val[1]

        bib_extra = {}
        parse_stack = ['{']

        for line in self.bib_file:
            if re.match(r'.*}',line):
                parse_stack.pop()
            if re.match(r'.*{',line):
                parse_stack.append('{')
            if len(parse_stack) == 0:
                """ Entry exit """
                if len(bib_extra) > 0:
                    self.entry[u'extras'] = bib_extra
                    bib_extra = []
                key_val = []
                print
                print "Entry: "
                for i in self.entry:
                    print i," = ", self.entry[i]
                extras_doc_funcs.insert_doc(self.entry)
                self.entry = {}
                break

            key_val = re.split(bibtex.BIBTEX_SPLIT, line)
            key_val = self.__clean_list(key_val)

            if len(key_val) < 2:
                continue

            bib_value = ''
            key_val[0] = key_val[0].lower()
            if key_val[0] == 'book':
                print "hier ist ein Fehler!",line
            elif key_val[0] == 'author' or key_val[0] == 'keywords':
                """ Multi-Value Fields """
                bib_field = bibtex.BIB_FIELDS[key_val[0]]
                key_val.remove(key_val[0])
                self.entry[bib_field] = key_val
            elif key_val[0]  == 'price':
                """ TODO: split in currency & price"""
                pass
            elif key_val[0] == u'dateofpurchase':
                if len(key_val) > 2:
                    raise ValueError()
#               TODO: Sofort auf Date arbeiten statt auf Datetime
                mydatetime = datetime.strptime(
                        key_val[1],'%d.%m.%Y')
                self.entry[bibtex.BIB_FIELDS[key_val[0]]] = mydatetime.date()
            elif key_val[0] in bibtex.BIB_FIELDS:
                """ Default Fields """
                if len(key_val) > 2:
                    """ value wurde zu weit zerlegt """
                    bib_value = self.__clean_list(
                            re.split(r"=", 
                            line,
                            maxsplit=2))[1]
                else:
                    bib_value = key_val[1]
                self.entry[bibtex.BIB_FIELDS[key_val[0]]] = bib_value
            else:
                """ Extra Field """
                if len(key_val) > 2:
                    """ value wurde zu weit zerlegt """
                    key_val = self.__clean_list(re.split(
                        r'=',
                        line,
                        maxsplit=2
                        ))
                bib_extra[key_val[0]] = key_val[1]

    def __clean_list(self, dirty_list):
        """ Entfernt die leeren Elemente aus einer Liste.

        """
        for i in range(len(dirty_list)):
            """ Bäääh, aber die Wahrscheinlichkeit wurde als gering eingestuft,
            dieser Schritt öfter widerholt werden muss - INTEL """
            dirty_list[i] = dirty_list[i].strip()
            dirty_list[i] = dirty_list[i].strip('"{},')
            dirty_list[i] = dirty_list[i].strip()
        while '' in dirty_list:
            dirty_list.remove('')
        return dirty_list
