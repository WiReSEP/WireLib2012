# vim: set fileencoding=utf-8
class UnknownCategoryError(Exception):
    """
    Einfügen eines Dokumentes mit einer Kategorie, die nicht in der Datenbank
    hinterlegt ist.
    """
    def __init__(self, cat):
        self.category = cat

class DuplicateKeyError(Exception):
    """
    Einfügen eines Dokumentes in die Datenbank, dessen bib_no schon vorhanden
    ist.
    """
    def __init__(self, message):
        self.reason = message

class LendingError(Exception):
    """
    Versuch des Ausleihens bei Status 'bestellt'
    """
    pass

class ExportError(Exception):
    """
    Fehler beim Export zu BibTeX oder Allegro
    """
    pass
