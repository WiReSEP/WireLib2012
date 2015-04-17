from documents.models import Document
from datetime import datetime

def update_allegro():
    file_keys = open(u"documents/lib/first_line", "r")
    date = datetime.today()
    date = date.date()
    for line in file_keys:
        line = line.strip()
        print "handling", line
        try :
            doc = Document.objects.filter(bib_no=line)
            doc.update(ub_date=date)
        except BaseException, e:
            print e
    file_keys.close()
    print "done"
