#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Got irritated enough to base this counter on bill katz' api and nick johnson's
# code and idea.
# Copyright (c) 2009 happychickoo.
#
# The MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from google.appengine.api import memcache
from google.appengine.ext import db

DEFAULT_UPDATE_INTERVAL = 10
DEFAULT_INITIAL_VALUE = 0

class CachedCounter(db.Model):
    counter = db.IntegerProperty(default=0)
    
class CachingCounter(object):
    def __init__(self, name, update_interval=DEFAULT_UPDATE_INTERVAL):
        self.key_name = name
        self.update_interval = update_interval

    def get_count(self):
        return CachingCounter.__get_entity_by_key_name(self.key_name).counter

    def set_count(self, value):
        CachingCounter.__set(self.key_name, value)
    count = property(fget=get_count, fset=set_count)

    def incr(self, delta=1, initial_value=DEFAULT_INITIAL_VALUE):
        CachingCounter.__incr(self.key_name, delta, initial_value, self.update_interval)

    def decr(self, delta=1, initial_value=DEFAULT_INITIAL_VALUE):
        CachingCounter.__decr(self.key_name, delta, initial_value, self.update_interval)

    # For api compatibility.
    increment = incr
    decrement = decr


    @classmethod
    def __get_entity_by_key_name(cls, key_name):
        entity = CachedCounter.get_by_key_name(key_name)
        if not entity:
            entity = CachedCounter(key_name=key_name)
        return entity
        

    @classmethod
    def __set(cls, name, value, update_interval=DEFAULT_UPDATE_INTERVAL):
        """
        Sets a memcached counter.
        """
        lock_key = "counter_lock:%s" % (name,)
        count_key = "counter_value:%s" % (name,)
        if memcache.add(lock_key, None, time=update_interval):
            # Time to update the DB
            #count = int(memcache.get(count_key) or initial_value) - delta
            def tx():
                #entity = db.get(key)
                entity = CachingCounter.__get_entity_by_key_name(name)
                entity.counter = value
                entity.put()
            db.run_in_transaction(tx)
            memcache.delete(count_key)
        else:
            # Just update memcache
            memcache.set(count_key, value=value)


    @classmethod
    def __incr(cls, name, delta=1, initial_value=DEFAULT_INITIAL_VALUE, update_interval=DEFAULT_UPDATE_INTERVAL):
        """Increments a memcached counter."""
        lock_key = "counter_lock:%s" % (name,)
        count_key = "counter_value:%s" % (name,)
        if memcache.add(lock_key, None, time=update_interval):
            # Time to update the DB
            count = int(memcache.get(count_key) or initial_value) + delta
            def tx():
                #entity = db.get(key)
                entity = CachingCounter.__get_entity_by_key_name(name)
                entity.counter += count
                entity.put()
            db.run_in_transaction(tx)
            memcache.delete(count_key)
        else:
            # Just update memcache
            memcache.incr(count_key, delta=delta, initial_value=initial_value)


    @classmethod
    def __decr(cls, name, delta=1, initial_value=DEFAULT_INITIAL_VALUE, update_interval=DEFAULT_UPDATE_INTERVAL):
        """Decrements a memcached counter."""
        lock_key = "counter_lock:%s" % (name,)
        count_key = "counter_value:%s" % (name,)
        if memcache.add(lock_key, None, time=update_interval):
            # Time to update the DB
            count = int(memcache.get(count_key) or initial_value) - delta
            def tx():
                #entity = db.get(key)
                entity = CachingCounter.__get_entity_by_key_name(name)
                entity.counter += count
                entity.put()
            db.run_in_transaction(tx)
            memcache.delete(count_key)
        else:
            # Just update memcache
            memcache.decr(count_key, delta=delta, initial_value=initial_value)
