import logging
import imaplib
import sys
import datetime
import email.header
from email.parser import HeaderParser
import re

class Imap_Server(object):

    def __init__(self, server, username, password, logger):
        self.logger = logger
        self._connect(server, username, password)

    def _connect(self, server, username, password):
        self.server = server
        self.username = username

        self.logger.debug("Connecting %s imap server with %s user" % (server, username))
        try:
            self.conn = imaplib.IMAP4_SSL(server)
        except imaplib.IMAP4.error:
            self.logger.critical("Can't connect to \"%s\"" % server)
            sys.exit()

        try:
            self.conn.login(username, password)
        except imaplib.IMAP4.error:
            self.logger.critical("Authentication problem while connecting to \"%s\"" % server)
            sys.exit()
        self.logger.debug("Successfully connected %s imap server with %s user" % (server, username))

    def list_folders(self):
        print "\n\nListing folders for %s/%s" % (self.server, self.username)
        typ, folders = self.conn.list()
        for folder in folders:
            print self._parse_list_folder(folder)
        
    def _parse_list_folder(self, line):
        list_response_pattern = re.compile(r'\((?P<flags>.*?)\) "(?P<delimiter>.*)" (?P<name>.*)')
        flags, delimiter, folder = list_response_pattern.match(line).groups()
        folder = folder.strip('"')
        typ, data = self.conn.status(folder, '(MESSAGES UNSEEN)')
        return data

    def select_folder(self, folder):
        self.folder = folder
        result = self.conn.select(folder)
        self.logger.info("%s has %s messages" %  (folder, result[1][0]))

    def get_uids(self, since=None, before=None):
        if since and before:
            self.logger.debug("since and before is provided")
            type, data = self.conn.uid('Search', None, 
                        '(SINCE {since} BEFORE {before})'.format(since=since, before=before))
        elif since:
            type, data = self.conn.uid('Search', None, 
                        '(SINCE {since})'.format(since=since))
        elif before:
            type, data = self.conn.uid('Search', None, 
                        '(BEFORE {before})'.format(before=before))
        else:
            typ, data = self.conn.uid('Search', None, 'ALL')
        uids = data[0].split()
        return uids

    def report(self):
        uids = self.get_uids()
        f_date = self.get_date(uids[0])
        l_date = self.get_date(uids[-1])
        print "uids[%s..%s] (%s mails, between %s and %s)" % (uids[0], uids[-1], 
                                                              len(uids), 
                                                              f_date, l_date)
        
    def get_date(self, uid):
        parser = HeaderParser()
        
        try:
            typ, header = self.conn.uid('fetch', uid, '(BODY[HEADER.FIELDS (DATE SUBJECT)])')
            headerdic = parser.parsestr(header[0][1])
            pz = email.utils.parsedate_tz(headerdic["Date"])
            stamp = email.utils.mktime_tz(pz)
            date = imaplib.Time2Internaldate(stamp)

            return date

        except:
            self.logger.error("Message date can't be found in the message")
            return None
            


    def get_message(self, uid):
        typ, data = self.conn.uid('fetch', uid, '(RFC822)')
        return data[0][1]

    def write_message(self, message):
        msg = email.message_from_string(message)

        try:
            pz = email.utils.parsedate_tz(msg['Date'])
            stamp = email.utils.mktime_tz(pz)
            date = imaplib.Time2Internaldate(stamp)
        except:
            self.logger.error("Message date can't be found in the message, using 1-Jan-2000")
            date = '"01-Jan-2000 00:00:00 +0000"'

        decode = email.header.decode_header(msg['Subject'])[0]
        try:
            subject = unicode(decode[0])
            self.logger.debug("Message: %s" % subject)
        except:
            self.logger.debug("Can't read subject")
            
        self.conn.append(self.folder, None, date, message)

    def close(self):
        if self.conn.state == 'SELECTED':            
            self.conn.close()
            self.conn.logout()
