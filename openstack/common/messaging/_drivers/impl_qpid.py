# Copyright 2013 Red Hat, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

""" Qpid Implementation."""

import functools
import itertools
import time
import uuid

import eventlet
import greenlet
from oslo.config import cfg

from openstack.common.gettextutils import _
from openstack.common import importutils
from openstack.common import jsonutils
from openstack.common import log as logging
from openstack.common.messaging._drivers import base

qpid_messaging = importutils.try_import("qpid.messaging")
qpid_exceptions = importutils.try_import("qpid.messaging.exceptions")

LOG = logging.getLogger(__name__)

qpid_opts = [
    cfg.StrOpt('qpid_hostname',
               default='localhost',
               help='Qpid broker hostname'),
    cfg.IntOpt('qpid_port',
               default=5672,
               help='Qpid broker port'),
    cfg.ListOpt('qpid_hosts',
                default=['$qpid_hostname:$qpid_port'],
                help='Qpid HA cluster host:port pairs'),
    cfg.StrOpt('qpid_username',
               default='',
               help='Username for qpid connection'),
    cfg.StrOpt('qpid_password',
               default='',
               help='Password for qpid connection',
               secret=True),
    cfg.StrOpt('qpid_sasl_mechanisms',
               default='',
               help='Space separated list of SASL mechanisms to use for auth'),
    cfg.IntOpt('qpid_heartbeat',
               default=60,
               help='Seconds between connection keepalive heartbeats'),
    cfg.StrOpt('qpid_protocol',
               default='tcp',
               help="Transport to use, either 'tcp' or 'ssl'"),
    cfg.BoolOpt('qpid_tcp_nodelay',
                default=True,
                help='Disable Nagle algorithm'),
]

cfg.CONF.register_opts(qpid_opts)


class QPIDDriver(base.BaseDriver):

    def __init__(self, conf, url=None, default_exchange=None):
        super(QPIDDriver, self).__init__(conf, url, default_exchange)
        self.connection = None
        self._brokers = conf.qpid_hosts

    def _create_connection(self, broker):
        # Create the connection - this does not open the connection
        self.connection = qpid_messaging.Connection(broker)

        # Check if flags are set and if so set them for the connection
        # before we call open
        self.connection.username = self.conf.qpid_username
        self.connection.password = self.conf.qpid_password

        self.connection.sasl_mechanisms = self.conf.qpid_sasl_mechanisms
        # Reconnection is done by self.reconnect()
        self.connection.reconnect = False
        self.connection.heartbeat = self.conf.qpid_heartbeat
        self.connection.transport = self.conf.qpid_protocol
        self.connection.tcp_nodelay = self.conf.qpid_tcp_nodelay

    def _reconnect(self):
        attempt = 0
        delay = 1
        while True:
            # Close the session if necessary
            if self.connection and self.connection.opened():
                try:
                    self.connection.close()
                except qpid_exceptions.ConnectionError:
                    pass

            broker = self._brokers[attempt % len(self.brokers)]
            attempt += 1

            try:
                self._create_connection(broker)
                self.connection.open()
            except qpid_exceptions.ConnectionError as e:
                msg_dict = dict(e=e, delay=delay)
                msg = _("Unable to connect to AMQP server: %(e)s. "
                        "Sleeping %(delay)s seconds") % msg_dict
                LOG.error(msg)
                time.sleep(delay)
                delay = min(2 * delay, 60)
            else:
                LOG.info(_('Connected to AMQP server on %s'), broker)
                break

    @property
    def session(self):
        try:
            if not self.connection.opened():
                self._reconnect()
            return self.connection.session()
        except AttributeError:
            self._reconnect()

        return self.connection.session()

    def _send(self, target, message, wait_for_reply=None, timeout=None):
        session = self.session

    def _listen(self, target):
        pass
