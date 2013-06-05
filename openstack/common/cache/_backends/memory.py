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


from openstack.common.cache import backends
from openstack.common import timeutils


class MemoryBackend(backends.BaseCache):

    def __init__(self, conf, cache_prefix):
        super(MemoryBackend, self).__init__(conf, cache_prefix)
        self.cache = {}

    def set(self, key, value, ttl=0):
        timeout = 0
        if ttl != 0:
            timeout = timeutils.utcnow_ts() + ttl
        self.cache[key] = (timeout, value)
        return True

    def get(self, key, default=None):
        now = timeutils.utcnow_ts()
        for k in self.cache.keys():
            (timeout, _value) = self.cache[k]
            if timeout and now >= timeout:
                del self.cache[k]

        return self.cache.get(key, (0, None))[1]

    def unset(self, key):
        self.cache.pop(key, None)
