import smtplib
import imaplib

#--
#gmail_user     = 'w4d4f4k.video@gmail.com'
#gmail_password = 'kJ5klOo9'
gmail_user = 'blazkqs@gmail.com'
gmail_password = 'j3kAt0mM'

sent_from = gmail_user
to        = ['w4d4f4k@gmail.com']
subject   = 'Hello world.'
body      = "Hey, what's up?\n\n"

email_text = """\
From: %s
To: %s
Subject: %s

%s
""" % (sent_from, ", ".join(to), subject, body)

#-- reading
"""
try:
    mail=imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(gmail_user,gmail_password)
    #mail.select('inbox')
    mail.select()
    t,d=mail.search(None,'ALL')
    #mail_ids=data[0]
    #id_list=mail_ids.split()
    for n in d[0].split():
        t,d = mail.fetch(n,'(RFC822)')
        #print("msg: {}\n{}\n".format(n,d[0][1]))
        print("msg: {}\n".format(d[0][1]))
    mail.close()
    mail.logout()
    print("data: {}".format(d))
except:
    print("Reading failed.")
"""

#-- sending
try:
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(gmail_user, gmail_password)
    server.sendmail(sent_from, to, email_text)
    server.close()

    print('Email sent!')
except Exception as e:
    print('Something went wrong...',e)

