# -*- coding: utf-8 -*-
"""
Created on Sun Jan 11 12:57:13 2015

@author: FMcGowran
"""

# import required librarires
# NB external libs have been avoided to be as portable as possible
# Import smtplib for the actual sending function
import imaplib
import smtplib
#import ConfigParser
from email.mime.text import MIMEText


# Default values for variables
SUBJECT = "XMLTV Parser issue"
SENDER = "cablewatch@inbox.com"
USERNAME = "cablewatch@inbox.com"
PASSWORD = "q1ur;nfaq1ur;nfa"
SMTP_SERVER = "my.inbox.com"
RECIPIENTS = "fran.mcgowran@gmail.com"

def open_imap4_connection(smtp_server = SMTP_SERVER, username = USERNAME,
                          password = PASSWORD, verbose=False):
    """
    Generic imap4_connection creator
    """
    # Connect to the server
#    smtp_server = config.get('server', 'smtp_server')
    if verbose: print ('Connecting to', smtp_server)
    connection = imaplib.IMAP4_SSL(smtp_server)

    # Login to our account
    #username = config.get('account', 'username')
    #password = config.get('account', 'password')
    if verbose: print ( 'Logging in as', username )
    connection.login(username, password)
    return connection

def send_mail( message, subject=SUBJECT, sender=SENDER,
              username = USERNAME, password = PASSWORD,
              receivers=RECIPIENTS, smtp_server=SMTP_SERVER ) :
    """
    Function to send a pop3 mail
    maybe flesh this out as a wrapper to IMAP & POP3 ...
    """

    # Create a text/plain message
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receivers

    # Send the message via smtp_server, 
    # but don't include the envelope header.
    s = smtplib.SMTP(smtp_server)
    # inbox.com doesn't support SSL/TLS    
    #s.starttls()
    s.login(username, password)
    s.sendmail(sender, receivers, msg.as_string())
    s.quit()

    return