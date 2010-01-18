#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

    def __get_entity_by_key_name(self, key_name):
        entity = CachedCounter.get_by_key_name(key_name)
        if not entity:
            entity = CachedCounter(key_name=self.key_name)
            entity.put()
        return entity

    def incr(self, delta=1, initial_value=DEFAULT_INITIAL_VALUE):
        cached_counter = self.__get_entity_by_key_name(self.key_name)
        key = cached_counter.key()
        CachingCounter.__incr(key, delta, initial_value, self.update_interval)

    def decr(self, delta=1, initial_value=DEFAULT_INITIAL_VALUE):
        cached_counter = self.__get_entity_by_key_name(self.key_name)
        key = cached_counter.key()
        CachingCounter.__decr(key, delta, initial_value, self.update_interval)

    @classmethod
    def __incr(cls, key, delta=1, initial_value=DEFAULT_INITIAL_VALUE, update_interval=DEFAULT_UPDATE_INTERVAL):
        """Increments a memcached counter.
        Args:
        key: The key of a datastore entity that contains the counter.
        """

        lock_key = "counter_lock:%s" % (key,)
        count_key = "counter_value:%s" % (key,)
        if memcache.add(lock_key, None, time=update_interval):
            # Time to update the DB
            count = int(memcache.get(count_key) or initial_value) + delta
            def tx():
                entity = db.get(key)
                entity.counter += count
                entity.put()
            db.run_in_transaction(tx)
            memcache.delete(count_key)
        else:
            # Just update memcache
            memcache.incr(count_key, delta=delta, initial_value=initial_value)

    @classmethod
    def __decr(cls, key, delta=1, initial_value=DEFAULT_INITIAL_VALUE, update_interval=DEFAULT_UPDATE_INTERVAL):
        """Decrements a memcached counter.
        Args:
        key: The key of a datastore entity that contains the counter.
        """
        lock_key = "counter_lock:%s" % (key,)
        count_key = "counter_value:%s" % (key,)
        if memcache.add(lock_key, None, time=update_interval):
            # Time to update the DB
            count = int(memcache.get(count_key) or initial_value) - delta
            def tx():
                entity = db.get(key)
                entity.counter += count
                entity.put()
            db.run_in_transaction(tx)
            memcache.delete(count_key)
        else:
            # Just update memcache
            memcache.decr(count_key, delta=delta, initial_value=initial_value)
