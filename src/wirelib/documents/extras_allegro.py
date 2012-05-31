# vim: set fileencoding=utf-8
from documents.models import document
from documents.models import doc_extra
from datetime import datetime
def export_allegro():
    """
    Diese Methode gibt eine Datei mit den aktuell zu exportierenden Büchern im
    Allegro-Format zurück.
    """
    allegro_query = document.objects.select_related().filter(
            ub_date__isnull=True, 
            category__name__iexact='book', 
            status__lte=1)
    date = datetime.today()
    date = date.date()
    filename = u"WiReLib_" + date.strftime("%d-%m-%Y") + u".ADT"
    tmp_file = open(filename, "w")
    # allegro_query.update(ub_date=date)
    print len(list(allegro_query))
    for doc in list(allegro_query):
        print >> tmp_file, u"#00"
        print >> tmp_file, __doc_to_string(doc).encode("iso-8859-1", "strict")
        print >> tmp_file, u""
        doc.save()
    tmp_file.close()
    return tmp_file

def __doc_to_string(document):
    """
    Diese Methode übernimmt die Erstellung des richtigen Export-Formates der
    einzelnen Dokumente
    """
    extra_fields = document.doc_extra_set.all()
    keywords_db = document.keywords_set.all()
    authors = list(document.authors.all())
    file_allegro_dict = open(u"documents/dict_allegro.txt", "r")
    allegro_dict = {}
    for line in file_allegro_dict:
        line = line.strip()
        tmp_list = line.split(u" ")
        allegro_dict[tmp_list[0]] = tmp_list[1]
    file_allegro_dict.close()
    line_end = u"\n"
    doc_str = u"" + allegro_dict[u"isbn"] + u" " + document.isbn + line_end
    doc_str += allegro_dict[u"publisher"] + u" " + document.publisher.name + line_end
    try:
        vol = extra_fields.get(bib_field__iexact="volume")
        vol = vol.content
    except doc_extra.DoesNotExist:
        vol = u""
    print "vol:", allegro_dict[u"volume"]
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
        locn = ""
    doc_str += allegro_dict[u"LibraryOfCongressNo"] + u" "
    doc_str += locn + line_end
    doc_str += allegro_dict[u"bookid"] + u" " + document.bibtex_id + line_end
    doc_str += allegro_dict[u"title"] + u" " + document.title + line_end
    doc_str += allegro_dict[u"address"] + u" " + document.address + line_end
    """
    hier werden die keywords in das richtige String-Format gebracht
    """
    keywords_list = []
    for k in keywords_db:
        keywords_list.append(k.keyword)
    keywords = "| ".join(keywords_list)
    doc_str += allegro_dict[u"keywords"] + u" " + keywords + line_end
    doc_str += allegro_dict[u"year"] + u" " + str(document.year) + line_end
    return doc_str
