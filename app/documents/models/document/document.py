# vim: set fileencoding=utf-8
from __future__ import unicode_literals

from ..bibtex import Category
from ..user import NonUser
from .author import Author
from .publisher import Publisher
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.db import models
from documents.lib.bibtex import Bibtex
from documents.lib.exceptions import LendingError
from django.core import validators


class Document(models.Model):
    AVAILABLE = 0   # vorhanden
    LEND = 1        # ausgeliehen
    ORDERED = 2     # bestellt
    MISSING = 3     # vermisst
    LOST = 4        # verloren

    CSS_CLASSES = {AVAILABLE: 'status-avail',
                   LEND: 'status-lend',
                   ORDERED: 'status-ordered',
                   MISSING: 'status-miss',
                   LOST: 'status-lost',
                   }

    STATUS_CHOICES = {AVAILABLE: "Verfügbar",
                      LEND: "Verliehen",
                      ORDERED: "Bestellt",
                      MISSING: "Vermisst",
                      LOST: "Verloren",
                      }

    bib_no = models.CharField("Bibliotheks-Nr.",
                              max_length=15,
                              primary_key=True,
                              validators=[
                                  validators.RegexValidator(r'\w\d+',
                                                            u'Eingabe ist nicht zulässig. Es wird ein '
                                                            u'Buchstaben geflogt von Zahlen erwartet. z.B. J110.'
                                                            )
                              ])
    inv_no = models.CharField("Inventar-Nr.", max_length=15, unique=True)
    bibtex_id = models.CharField("Bibtex-ID", max_length=120, unique=True)
    lib_of_con_nr = models.CharField("Library Of Congress No",
                                     max_length=60,
                                     blank=True,
                                     null=True)
    price = models.DecimalField("Preis",
                                max_digits=6,
                                decimal_places=2,
                                blank=True,
                                null=True)
    currency = models.CharField("Währung",
                                max_length=10,
                                blank=True,
                                null=True)
    title = models.CharField("Titel", max_length=255)
    status = models.IntegerField("Status", null=True,
                                 choices=STATUS_CHOICES.items(),
                                 default=AVAILABLE)
    isbn = models.CharField("ISBN", max_length=17, blank=True, null=True)
    category = models.ForeignKey(Category, verbose_name="Kategorie")
    last_updated = models.DateField("Zuletzt geupdated", auto_now=True)
    last_edit_by = models.ForeignKey(get_user_model(),
                                     verbose_name="Zuletzt geändert von")
    publisher = models.ForeignKey(Publisher, blank=True, null=True)
    year = models.IntegerField("Jahr", blank=True, null=True)
    address = models.CharField(
        "Adresse", max_length=100, blank=True, null=True)
    date_of_purchase = models.DateField("Kaufdatum", auto_now_add=True)
    ub_date = models.DateField("UB-Export", blank=True, null=True)
        # Datum des Allegro-Exports
    bib_date = models.DateField("BibTeX-Export", blank=True, null=True)
        # Datum des BibTeX-Exports
    comment = models.TextField("Kommentar", blank=True, null=True)
    authors = models.ManyToManyField(Author, through='DocumentAuthors',
                                     verbose_name="Autoren")

    class Meta:
        app_label = "documents"
        permissions = (("can_see_price", "Can see price"),
                       ("can_see_locn", "Can see library of congress number"),
                       ("can_see_last_update_info",
                        "Can see last update info"),
                       ("can_see_dop", "Can see date of purchase"),
                       ("can_see_export", "Can see dates of export"),
                       ("can_import", "Can import documents"),
                       ("can_export", "Can export documents"),)
        ordering = ['title']
        verbose_name = "Dokument"
        verbose_name_plural = "Dokumente"

    def save(self, user=None, *args, **kwargs):
        """
        Methode zum Speichern des letzten Bearbeiters des Dokumentes
        """
        if user is None:
            user = get_user_model().objects.get(id=1)
        self.last_edit_by = user
        super(Document, self).save(*args, **kwargs)
        if not self.status == self._status():
            self.set_status(user, self.status)

    def _status(self):
        """
        Ausgeben des aktuellen Status'
        """
        try:
            retVal = self.docstatus_set.latest('date').status
        except BaseException:
            retVal = Document.AVAILABLE
        return retVal

    def __init__(self, *args, **kwargs):
        models.Model.__init__(self, *args, **kwargs)
#        self.status = self._status()

    def __unicode__(self):
        return self.title

    def set_status(self,
                   editor,
                   stat,
                   terminate=None,
                   user=None,
                   non_user=None):
        """
        Methode zum Ändern des Status'
        Paramenter:
            editor - recent_user
            stat - status
            terminate - date_term_lend
            user - user_lend
            non_user - non_user_lend
        """
        try:  # Wenn es was zum updaten gibt:
            old = self.docstatus_set.latest('date')
            # bei F5-Benutzung eines Buttons wurden zwei Einträge eingefügt und
            # beide waren so gekennzeichnet, dass es keinen Nachfolgeeintrag
            # gäbe
            if not (old.status == stat
                    and old.recent_user == editor
                    and old.user_lend == user
                    and old.non_user_lend == non_user):
                old.return_lend = True
                old.save()
        except DocStatus.DoesNotExist:
            # There is no DocStatus. Maybe the Document has just been imported.
            # So there is no need to do anything right now, new status is coming
            # now.
            pass
        if stat == Document.LEND and user is None:
            user = editor
        l = DocStatus(
            recent_user=editor,
            doc_id=self,
            status=stat,
            date_term_lend=terminate,
            user_lend=user,
            non_user_lend=non_user)
        l.save()
        if not self.status == stat:
            self.status = stat
            self.save()

    def lend(self, user, editor=None, non_user=None, terminate=None):
        """
        Methode zum Ausleihen, Übertragen und beim Wiederfinden
        Parameter:
            user - user_lend (evtl recent_user)
            editor - recent_user
            non_user - non_user_lend
            terminate - date_term_lend
        """
        # fürs Übertragen
        if self.status == Document.LEND:
            dstat = self.docstatus_set.latest('date')
            if dstat.user_lend == user and dstat.non_user_lend == non_user:
                return
        # zum Ausleihen oder Wiederfinden
        elif self.status == Document.ORDERED:
            raise LendingError()
        if editor is None:
            editor = user
        self.set_status(editor, Document.LEND, terminate, user, non_user)

    def unlend(self, user):
        """
        Methode zum zurückgeben
        """
        self.set_status(user, Document.AVAILABLE)

    def lost(self, user):
        """
        Methode zum "Verloren" setzen
        """
        self.set_status(user, Document.LOST)

    def missing(self, user):
        """
        Methode für Vermisstmeldungen
        """
        self.set_status(user, Document.MISSING)

    def _order_authors(self, auths):
        return auths.order_by("documentauthors__sort_value")

    def get_all_authors(self):
        """
        Methode um alle Autoren und Editoren anzuzeigen
        """
        auths = self.authors.all()
        auths = self._order_authors(auths)
        editors = self.get_editors()
        for a in auths:
            if editors.filter(pk=a.pk):
                a.editor = True
        return auths

    def get_editors(self):
        """
        Methode um alle Editoren anzuzeigen
        """
        auths = self.authors.filter(documentauthors__editor=True)
        return self._order_authors(auths)

    def get_authors(self):
        """
        Methode um alle Autoren anzuzeigen
        """
        auths = self.authors.exclude(documentauthors__editor=True)
        return self._order_authors(auths)

    def add_author(self, author):
        """
        Methode um dem Dokument einen Autoren zuzuweisen
        """
        self._add_author_or_editor(author, False)

    def add_editor(self, editor):
        """
        Methode um dem Dokument einen Autoren als Editor zuzuweisen
        """
        self._add_author_or_editor(editor, True)

    def _add_author_or_editor(self, obj, is_editor):
        from django.db.models import Max
        params = dict()
        connections = DocumentAuthors.objects.filter(
            document=self, editor=is_editor)
        max_val = connections.aggregate(Max('sort_value'))["sort_value__max"]
        if max_val is None:
            max_val = 0
        else:
            max_val = max_val + 1
        params["sort_value"] = max_val + 1
        d, dummy = DocumentAuthors.objects.get_or_create(document=self,
                                                         author=obj, editor=is_editor, sort_value=max_val)
        d.save()

    def is_available(self):
        return self.status == Document.AVAILABLE

    def is_lend(self):
        return self.status == Document.LEND

    def is_missing(self):
        return self.status == Document.MISSING

    def is_lost(self):
        return self.status == Document.LOST

    def get_user_lend(self):
        if not self.is_lend():
            return get_user_model.objects.None()
        latest = self.docstatus_set.latest('date')
        if latest:
            retVal = latest.recent_user
            if latest.user_lend:
                retVal = latest.user_lend
            if latest.non_user_lend:
                retVal = latest.non_user_lend
        else:
            retVal = get_user_model().objects.None()
        return retVal

    def get_user_responsible(self):
        if not self.is_lend():
            return get_user_model.objects.None()
        latest = self.docstatus_set.latest('date')
        if latest:
            retVal = latest.recent_user
            if latest.user_lend:
                retVal = latest.user_lend
        else:
            retVal = get_user_model().objects.None()
        return retVal

    def get_status_css_class(self):
        return Document.CSS_CLASSES[self.status]

    def get_status_string(self):
        return Document.STATUS_CHOICES[self.status]

    def get_bibtex(self):
        return Bibtex.export_doc(self)

    def get_absolute_url(self):
        return reverse('documents.detail', args=(self.pk,))


class DocumentAuthors(models.Model):
    document = models.ForeignKey(Document)
    author = models.ForeignKey(Author, verbose_name="Autor")
    editor = models.BooleanField(default=False)
    sort_value = models.IntegerField("Reihenfolge")
    _sort_field_name = "sort_value"

    class Meta:
        app_label = "documents"
        verbose_name = "Dokument Autoren"
        verbose_name_plural = "Dokument Autoren"
        unique_together = ('document', 'author')

    def __unicode__(self):
        return u'%s/%s' % (self.document, self.author)


class DocStatus(models.Model):
        # auftraggebender User
    recent_user = models.ForeignKey(get_user_model(),
                                    related_name='recent_user')
    doc_id = models.ForeignKey(Document)
        # in welchen Status wurde geändert?
    status = models.IntegerField(choices=Document.STATUS_CHOICES.items(),
                                 default=Document.AVAILABLE)
        # Datum an dem es geschah
    date = models.DateTimeField(auto_now_add=True)
        # False markiert den aktuellsten Eintrag für den Status eines
        # Dokumentes
    return_lend = models.BooleanField(default=False)
        # Ende der Rückgabefrist
    date_term_lend = models.DateTimeField(blank=True, null=True)
        # ausleihender User
    user_lend = models.ForeignKey(get_user_model(), blank=True,
                                  null=True, related_name='user_lend')
        # ausleihender non_User
    non_user_lend = models.ForeignKey(NonUser, blank=True, null=True)

    def get_status_string(self):
        return Document.STATUS_CHOICES[self.status]

    class Meta:
        app_label = "documents"
        permissions = (("can_lend", "Can lend documents"),
                       ("can_unlend", "Can unlend documents"),
                       ("can_miss", "Can miss documents"),
                       ("can_order", "Can order documents"),
                       ("can_lost", "Can lost documents"),
                       ("can_see_history", "Can see documenthistory"),)
