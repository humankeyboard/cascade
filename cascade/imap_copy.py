import os
import logging
import ConfigParser
import datetime
from progressbar import ProgressBar, Percentage, Bar, ETA, RotatingMarker
import time
from imap_server import Imap_Server

class Imap_Copy(object):

    def __init__(self, config_file='~/cascade.conf', log_level='WARNING'):
        self._logger(log_level)
        self._read_config(config_file)
        self._connect()

    def _logger(self, log_level):
        self.logger = logging.getLogger("cascade")
        self.logger.setLevel(log_level.upper())

        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s -> %(message)s')
        ch.setFormatter(formatter)

        self.logger.addHandler(ch)
    
    def get_logger(self):
        return self.logger

    def _read_config(self, config_file):
        self.config = ConfigParser.ConfigParser()

        if config_file == '~/cascade.conf':
            self.logger.debug("Default configuration file \"%s\" will be used" % config_file)

        try:
            with open(os.path.expanduser(config_file)) as file:
                pass
            self.config.read([os.path.expanduser(config_file)])
            self.logger.debug("Configuration file \"%s\" is read successfully" % config_file)
        except IOError:
            #logging.critical("Can't find %s" % (config_file))
            self.logger.critical("Can't find configuration file: \"%s\"" % config_file)
            exit(2)
        
    def print_config(self):
        print self.config

    def _connect(self):
        self.src_server = Imap_Server(self.config.get('Source', 'server'),
                                      self.config.get('Source', 'username'),
                                      self.config.get('Source', 'password'),
                                      self.logger)

        self.dst_server = Imap_Server(self.config.get('Destination', 'server'),
                                      self.config.get('Destination', 'username'),
                                      self.config.get('Destination', 'password'),
                                      self.logger)
        
    def list_folders(self):
        self.src_server.list_folders()
        self.dst_server.list_folders()

    def select_folder(self, folder=None):
        if not folder:
            self.src_server.select_folder(self.config.get('Source','folder'))
            self.dst_server.select_folder(self.config.get('Destination','folder'))
        else:
            self.src_server.select_folder(folder)

    def copy_message(self, uid):
        message = self.src_server.get_message(uid)
        self.dst_server.write_message(message)

    def copy_messages(self):
        since = None
        before = None

        if 'Dates' in self.config.sections():
            since = self.config.get('Dates', 'after')
            before = self.config.get('Dates', 'before')

        if since and before:
            d_since = datetime.datetime.strptime(since, '%d-%b-%Y')
            d_before = datetime.datetime.strptime(before, '%d-%b-%Y')
            if d_before < d_since:
                self.logger.error("Wrong dates, %s is older than %s" % (before, since))
                exit(2)

        uids = self.src_server.get_uids(since=since, before=before)
        counter = 0
        total = len(uids)

        if total == 0:
            print "No messages found"
        else:
            title = 'Copying  ' + str(total) + ' messages\n'
            widgets = [title, Percentage(), ' ', Bar("+"),
                       ' ', ETA()]
            pbar = ProgressBar(widgets=widgets, maxval=total).start()

            for uid in uids:
                message = self.src_server.get_message(uid)
                self.logger.debug("Message date: %s" % self.src_server.get_date(uid))
                self.dst_server.write_message(message)
                pbar.update(counter)
                counter = counter + 1
            print 'Finished ',
            sys.stdout.flush()


    def report(self):
        self.src_server.report()
        self.dst_server.report()

    def close(self):
        self.src_server.close()
        self.dst_server.close()

    def test(self):
        self.src_server.list_folders()
