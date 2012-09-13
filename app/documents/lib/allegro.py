# vim: set fileencoding=utf-8
import threading
from documents.models import document
from documents.models import doc_extra
from documents.lib.exceptions import ExportError
from datetime import datetime
from django.conf import settings

def export_allegro():
    """ Deprecated function. Es sollte die Klasse Allegro verwendet werden.
    """
    Allegro().doc_export()

class Allegro(threading.Thread):
    """ Threading fähige Klasse für den Allegro export.
    """
    docs_to_export = True
    """ static var um exceptions in anderen Threads verarbeiten zu können. Die
    Variable darf nicht für eine vorherige Bestimmung ob Dokumente exportiert
    werden können verwendet werden.
    """
    docs_to_export_lock = threading.Lock()
    """ Lock-Variable für docs_to_export
    """
    allegro_lock = threading.Lock()
    """ Stellt sicher, dass immer nur eine Instanz von Allegro läuft
    """

    def run(self):
        if Allegro.allegro_lock.locked():
            return
        Allegro.allegro_lock.acquire()
        self.doc_export()
        Allegro.allegro_lock.release()

    def doc_export(self):
        """
        Diese Methode gibt eine Datei mit den aktuell zu exportierenden Büchern im
        Allegro-Format zurück.
        """
        Allegro.docs_to_export = True
        allegro_query = document.objects.select_related().filter(
                ub_date__isnull=True, 
                category__name__iexact='book')
        if 0 == allegro_query.count():
            Allegro.docs_to_export_lock.acquire()
            Allegro.docs_to_export = False
            Allegro.docs_to_export_lock.release()
            raise ExportError("Keine Dokumente zum Exportieren")
        date = datetime.today()
        date = date.date()
        # einlesen der Hashmap für Speicherung von Einträgen im ADT-Format
        file_allegro_dict = open(u"documents/dict_allegro.txt", "r")
        allegro_dict = {}
        for line in file_allegro_dict:
            line = line.strip()
            tmp_list = line.split(u" ")
            allegro_dict[tmp_list[0]] = tmp_list[1]
        file_allegro_dict.close()
        filepath = settings.DOCUMENTS_SECDIR + settings.DOCUMENTS_ALLEGRO_FILES
#        filepath = getattr(settings, 'DOCUMENTS_ALLEGRO_FILES', "documents/exports/")
        filename = u"WiReLib_" + date.strftime("%d-%m-%Y") + u".ADT"
        # ab hier wird in die Datei geschrieben, iso-8859-1 für Kompatiblität
        tmp_file = open(filepath + filename, "w")
        for doc in list(allegro_query):
            if doc.status <= 1:
                print >> tmp_file, u"#00"
                print >> tmp_file, Allegro.__doc_to_string(doc, allegro_dict).encode("iso-8859-1", "strict")
        tmp_file.close()
        allegro_query.update(ub_date=date)
        for doc in allegro_query:
            doc.save()
        return tmp_file
    
    @staticmethod
    def __doc_to_string(document, allegro_dict):
        """
        Diese Methode übernimmt die Erstellung des richtigen Export-Formates der
        einzelnen Dokumente
        """
        extra_fields = document.doc_extra_set.all()
        keywords_db = document.keywords_set.all()
        authors = list(document.authors.all())
        line_end = u"\n"
        #speichern aller benötigten Feldinhalte in den Rückgabestring
        isbn = document.isbn
        if isbn == None:
            isbn = u""
        doc_str = u"" + allegro_dict[u"isbn"] + u" " + isbn + line_end
        doc_str += allegro_dict[u"publisher"] + u" "
        doc_str += document.publisher.name + line_end
        try:
            vol = extra_fields.get(bib_field__iexact="volume")
            vol = vol.content
        except doc_extra.DoesNotExist:
            vol = u""
        doc_str += u"" + allegro_dict[u"volume"] + u" " + vol + line_end
        try:
            series = extra_fields.get(bib_field__iexact="series")
            series = series.content
        except doc_extra.DoesNotExist:
            series = u""
        doc_str += allegro_dict[u"series"] + u" " + series + line_end
        auth = allegro_dict[u"author"]
        doc_str += auth + u" " + authors[0].last_name + u" , " 
        doc_str += authors[0].first_name + line_end
        if len(authors) > 1:
            j = 0
            for auth_i in authors[1:]:
                doc_str += auth + str(j) + u" " + auth_i.last_name + u", "
                doc_str += auth_i.first_name + line_end
                j += 1
        locn = document.lib_of_con_nr
        if locn == None:
            locn = u""
        doc_str += allegro_dict[u"LibraryOfCongressNo"] + u" "
        doc_str += locn + line_end
        doc_str += allegro_dict[u"bookid"] + u" " + document.bibtex_id + line_end
        doc_str += allegro_dict[u"title"] + u" " + document.title + line_end
        address = document.address
        if address == None:
            address = u""
        doc_str += allegro_dict[u"address"] + u" " + address + line_end
        # hier werden die keywords in das richtige String-Format gebracht
        keywords_list = []
        for k in keywords_db:
            keywords_list.append(k.keyword)
        keywords = "| ".join(keywords_list)
        doc_str += allegro_dict[u"keywords"] + u" " + keywords + line_end
        doc_str += allegro_dict[u"year"] + u" " + str(document.year) + line_end
        return doc_str
