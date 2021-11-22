#!/usr/bin/env python

import os
import re
import daemon
import asyncore
import smtpd
import logging
import smtplib

class SimpleRelayService(smtpd.PureProxy):
    """Handles processing mail for relay"""

    def __init__(self, config, bind, remote):
        smtpd.SMTPServer.__init__(self, bind, remote)
        self.config = config
        logging.basicConfig(filename=config['log_file'],
                            level=logging.DEBUG,
                            format="%(asctime)s %(levelname)s %(message)s")
        logging.info("Simple relay service started on %s:%s" % bind)

    def process_message(self, peer, mailfrom, rcpttos, data):
        logging.debug("Receieved a message from %s to %s" % (mailfrom, rcpttos))
        refused = self._deliver(mailfrom, rcpttos, data)
  
    def _deliver(self, mailfrom, rcpttos, data):
        refused = {}
        try:
            s = smtplib.SMTP(self._remoteaddr[0], self._remoteaddr[1], timeout=30)
            tls_flag = self.config['tls']
            if tls_flag == 'yes':
                s.starttls()
            if len(self._remoteaddr) > 2:
                s.login(self._remoteaddr[2], self._remoteaddr[3])
            try:
                refused = s.sendmail(mailfrom, rcpttos, data)
            finally:
                s.quit()
        except smtplib.SMTPRecipientsRefused as e:
            #print('got SMTPRecipientsRefused', file=DEBUGSTREAM)
            refused = e.recipients
        except (OSError, smtplib.SMTPException) as e:
            #print('got', e.__class__, file=DEBUGSTREAM)
            # All recipients were refused.  If the exception had an associated
            # error code, use it.  Otherwise,fake it with a non-triggering
            # exception code.
            errcode = getattr(e, 'smtp_code', -1)
            errmsg = getattr(e, 'smtp_error', 'ignore')
            for r in rcpttos:
                refused[r] = (errcode, errmsg)
        return refused

if __name__ == "__main__":

    log_file = 'simplerelay.log'
    if os.environ.has_key('LOG_FILE'):
        log_file = os.environ['LOG_FILE']

    bind = (os.environ['BIND_ADDRESS'], int(os.environ['BIND_PORT']))
    relay = (os.environ['RELAY_HOST'], int(os.environ['RELAY_HOST_PORT']))
    tls_flag = os.environ['RELAY_HOST_TLS']
    config = {
        'log_file': log_file,
        'rcpt_domain': '',
        'fwd_address': '',
        'tls': tls_flag}

    if os.environ.has_key('DAEMONIZE') and bool(os.environ['DAEMONIZE']):
        from daemon.pidlockfile import PIDLockFile
        pidfile = PIDLockFile(os.environ['PIDFILE'])
        working_directory = os.environ['WORKING_DIRECTORY']
        startup_log_file=open(log_file, 'a')
        with daemon.DaemonContext(pidfile=pidfile, working_directory=working_directory,
                                  stdout=startup_log_file, stderr=startup_log_file):
            smtp_server = SimpleRelayService(config, bind, relay)
            asyncore.loop()
    else:
        smtp_server = SimpleRelayService(config, bind, relay)
        try:
            asyncore.loop()
        except KeyboardInterrupt:
            smtp_server.close()
