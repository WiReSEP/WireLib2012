# vim: set fileencoding=utf-8
from documents.models import document
from documents.models import doc_extra
import datetime
def export_allegro():
    """
    Diese Methode gibt eine Datei mit den aktuell zu exportierenden Büchern im
    Allegro-Format zurück.
    """
    allegro_query = document.objects.select_related().filter(
            document__ub_date__isnull=True, 
            document__category__name__iexact='book', 
            document__status__lte=1)
    date = datetime.date.today()
    filename = "WiReLib", datetime.strftime("%d-%m-%Y", date) + ".ADT"
    tmp_file = open(filename, "w")
    allegro_query.update(ub_Date=date)
    for doc in allegro_query:
        print >> tmp_file, "#00"
        print >> tmp_file, __doc_to_string(doc)
        print >> tmp_file, ""
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
    authors = list(document.author_set.all())
    file_allegro_dict = open("dict_Allegro.txt", "r")
    allegro_dict = {}
    for line in file_allegro_dict:
        line = line.strip()
        tmp_list = line.split(" ")
        allegro_dict[tmp_list[0]] = tmp_list[1]
    file_allegro_dict.close()
    line_end = u"\n"
    doc_str = u"" + allegro_dict["isbn"], document.isbn + line_end
    doc_str += allegro_dict["publisher"], document.publisher.name + line_end
    try:
        vol = extra_fields.get(bib_field__iexact="volume")
    except doc_extra.DoesNotExist:
        vol = u""
    doc_str += allegro_dict["volume"], vol + line_end
    try:
        series = extra_fields.get(bib_field__iexact="series")
    except doc_extra.DoesNotExist:
        series = u""
    doc_str += allegro_dict["series"], series + line_end
    auth = allegro_dict["author"]
    doc_str += auth, authors[0].surname, u",", authors[0].name + line_end
    if len(authors) > 1:
        j = 0
        for auth_i in authors[1:]:
            doc_str += auth + j, auth_i.surname, u",", auth_i.name + line_end
            j += 1
    doc_str += (allegro_dict["LibraryOfCongressNo"], document.lib_of_con_nr
            + line_end)
    doc_str += allegro_dict["bookid"], document.bibtex_id + line_end
    doc_str += allegro_dict["title"], document.title + line_end
    doc_str += allegro_dict["address"], document.address + line_end
    """
    hier werden die keywords in das richtige String-Format gebracht
    """
    keywords_list = []
    for k in keywords_db:
        keywords_list.append(k.keyword)
    keywords = "| ".join(keywords_list)
    doc_str += allegro_dict["keywords"], keywords + line_end
    doc_str += allegro_dict["year"], document.pub_date.year + line_end
    return doc_str
