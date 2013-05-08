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

"""Multiple Cache API backend support.

Supported configuration options:

`cache_backend`: Name of the cache back-end to use.
"""

from oslo.config import cfg
from stevedore import driver

from openstack.common.cache import backends

_cache_options = [
    cfg.StrOpt('cache_backend',
               default='memory',
               help='The cache driver to use, defaults to memory. Other '
                    'drivers include redis and memcached.'),
    cfg.StrOpt('cache_prefix',
               default=None,
               help='Prefix to use in every cache key'),
]


def get_cache(conf):
    conf.register_opts(_cache_options)

    cache_backend = conf.cache_backend
    kwargs = dict(cache_prefix=conf.cache_prefix)

    mgr = driver.DriverManager(backends.NAMESPACE,
                               cache_backend,
                               invoke_on_load=True,
                               invoke_args=[conf],
                               invoke_kwds=kwargs)
    return mgr.driver
