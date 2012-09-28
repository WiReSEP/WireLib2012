# vim: set fileencoding=utf-8
sender_mail = "info@wirelib.sc.cs.tu-bs.de"

def _send_mail(receiver, subject, emailcontent, **context):
    connection = mail.get_conection()
    c = Context(context)
    text_content = emailcontent.render(c)
    for to in receiver:
        final_mail = mail.EmailMessage(subject,
                                   text_content,
                                   sender_mail,
                                   [to],
                                   connection=connection
                                   )
        final_mail.send()

def _document_missing_email(document, user):
    email = emails.objects.get(name="Vermisst Gemeldet")
    plaintext = Template(email.text)
    member = User.objects.values_list('email' flat=True)
    receiver = user.email
    c = Context({"document_name": document.title,
                 "user_name": user.first_name,
                 })
    subject = "[WiReLib] Vermisstmeldung"
    _send_mail([receiver], subject, plaintext, document_name=document.title,
            user_name=user.first_name)

def _document_expired_email(day_amount):
    current_day = datetime.date.today()
    expired_docs = doc_status.objects.filter(return_lend=False,
            date_term_lend__exact=current_day + datetime.timedelta(day_amount))
    user_email = emails.objects.get(name="Frist Erinerungsmail(B)")
    nonuser_email = emails.objects.get(name="Frist Erinnerungsmail(E)")
    plaintext_user = Template(user_email.text)
    plaintext_nonuser = Template(nonuser_email.text)

    # Vorbereiten der EMails

    for entry in expired_docs:
        _send_mail(receiver=[entry.user_lend.email],
                   subject=user_email.subject,
                   emailcontent=plaintext_user,
                   user_name=entry.user_lend.username,
                   document_name=entry.doc_id.title,
                   nonuser_firstname=entry.non_user_lend.firstname,
                   nonuser_lastname=entry.non_user_lend.lastname
                   )
        _send_mail(receiver=[entry.non_user_lend.email],
                   subject=nonuser_email.subject,
                   emailcontent=plaintext_user,
                   user_name=entry.user_lend.username,
                   document_name=entry.doc_id.title,
                   nonuser_firstname=entry.non_user_lend.firstname,
                   nonuser_lastname=entry.non_user_lend.lastname
                   )
