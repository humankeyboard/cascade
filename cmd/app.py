#!/usr/bin/env python

import ConfigParser
import argparse
import os, sys
from cascade import Imap_Copy


def app():
    parser = argparse.ArgumentParser(description='Copy mails from one imap server to another')
    parser.add_argument('-y', '--config', help='Configuration file', 
                        default='~/cascade.conf', 
                        required=False)
    parser.add_argument('-l', '--log-level', help='Log level', 
                        default='warning', 
                        choices=['debug', 'info', 'warning', 'error', 'critical'], 
                        required=False)
    parser.add_argument('-f', '--folders', help='List folders', 
                        action='store_true', default=False)
    parser.add_argument('-c', '--copy', help='Copy emails',
                        action='store_true', default=False)
    args = parser.parse_args()

    try:
        imap_copy = Imap_Copy(config_file=args.config, log_level=args.log_level)
        if args.folders:
            imap_copy.list_folders()
        if args.copy:
            imap_copy.select_folder()
            imap_copy.copy_messages()
    except KeyboardInterrupt:
        imap_copy.close()
        print "\nTerminated by user\n"


if __name__ == '__main__':
    app()
