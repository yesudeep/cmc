#!/usr/bin/env python
# -*- coding: utf-8; mode: python; tab-width: 4; indent-tabs-mode: nil; -*-
# Models for the datastore.
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

import configuration
from google.appengine.ext import db
from google.appengine.api import memcache
from aetycoon import TransformProperty
from django.template.defaultfilters import slugify
from caching_counter import CachingCounter

def serialize_entities(models):
    if models is None:
        return None
    elif isinstance(models, db.Model):
        # Just one instance
        return db.model_to_protobuf(models).Encode()
    else:
        # A list
        return [db.model_to_protobuf(x).Encode() for x in models]

def deserialize_entities(data):
    from google.appengine.datastore import entity_pb
    if data is None:
        return None
    elif isinstance(data, str):
        # Just one instance
        return db.model_from_protobuf(entity_pb.EntityProto(data))
    else:
        return [db.model_from_protobuf(entity_pb.EntityProto(x)) for x in data]

class SerializableModel(db.Model):
    """
    A model parent that includes properties and functionality
    common to many model classes.

    """
    is_deleted = db.BooleanProperty(default=False)
    is_starred = db.BooleanProperty(default=False)
    is_active = db.BooleanProperty(default=False)
    when_created = db.DateTimeProperty(auto_now_add=True)
    when_modified = db.DateTimeProperty(auto_now=True)

    def to_json_dict(self, *props):
        properties = self.properties()
        if props:
            serializable_properties = props
        else:
            serializable_properties = getattr(self, '__serialize__', [])
            if not serializable_properties:
                serializable_properties = properties.keys()
            else:
                serializable_properties.extend([
                    'is_deleted',
                    'is_starred',
                    'is_active',
                    'when_created',
                    'when_modified',
                    ])
        output = {}
        output['key'] = str(self.key())
        for prop in set(serializable_properties):
            v = properties[prop]
            if isinstance(v, db.DateTimeProperty) or isinstance(v, db.DateProperty):
                convert_function = (lambda d: d.strftime('%Y-%m-%dT%H:%M:%S'))
                output[prop] = convert_function(getattr(self, prop))
            elif isinstance(v, db.ReferenceProperty):
                str_key = str(getattr(self, prop).key())
                output[prop] = str_key
                #output[prop + '_key'] = str_key
            #elif isinstance(v, db.StringProperty):
            #    output[prop] = str(getattr(self, prop))
            #elif isinstance(v, db.BooleanProperty):
            #    output[prop] = bool(getattr(self, prop))
            else:
                output[prop] = getattr(self, prop)
        return output

    def to_json(self, *props):
        json_dict = self.to_json_dict(*props)
        return json.dumps(json_dict)


class OpenIDUser(SerializableModel):
    nickname = db.StringProperty()
    identifier = db.StringProperty(required=True)
    email = db.EmailProperty()

class SuggestedTitle(SerializableModel):
    title = db.StringProperty(required=True)
    slug = TransformProperty(title, slugify)
    
    def increment_vote_count(self, delta=1):
        CachingCounter('SuggestedTitle(%s).vote_count.key=%s' % (self.slug, str(self.key()))).incr(delta=delta)
    
    @property
    def vote_count(self):
        return CachingCounter('SuggestedTitle(%s).vote_count.key=%s' % (self.slug, str(self.key()))).count
    
    @classmethod
    def up_vote_or_insert(cls, title):
        t = SuggestedTitle.all().filter('slug = ', slugify(title)).get()
        if not t:
            t = SuggestedTitle(title=title)
            t.put()
        t.increment_vote_count()
        return t
        
class Celebrity(SerializableModel):
    name = db.StringProperty(required=True)
    slug = TransformProperty(name, slugify)
    
    def increment_vote_count(self, delta=1):
        CachingCounter('Celebrity(%s).vote_count.key=%s' % (self.slug, str(self.key()))).incr(delta=delta)
    
    @property
    def vote_count(self):
        return CachingCounter('Celebrity(%s).vote_count.key=%s' % (self.slug, str(self.key()))).count
    
    @classmethod
    def up_vote_or_insert(cls, name):
        t = Celebrity.all().filter('slug = ', slugify(name)).get()
        if not t:
            t = Celebrity(name=name)
            t.put()
        t.increment_vote_count()
        return t
    
    @classmethod
    def get_latest(cls, count=100):
        cache_key = 'Celebrity.get_latest(count=%d)' % count
        celebrities = deserialize_entities(memcache.get(cache_key))
        if not celebrities:
            celebrities = Celebrity.all().order('-when_modified').fetch(count)
            memcache.set(cache_key, serialize_entities(celebrities), 10)
        return celebrities

class Person(SerializableModel):
    full_name = db.StringProperty(required=True)
    email = db.EmailProperty(required=True)
    phone_number = db.StringProperty()

class SuggestedTitlePerson(Person):
    suggested_title = db.ReferenceProperty(SuggestedTitle, collection_name='people')

class StoryAuthor(Person):
    pass

class NotifyReleasePerson(Person):
    pass

class Story(SerializableModel):
    title = db.StringProperty(required=True)
    content = db.TextProperty(default=db.Blob(""))
    author = db.ReferenceProperty(StoryAuthor, collection_name="stories")
    
    def get_latest_document(self):
        """Returns the latest document submitted."""
        pass

class StoryDocument(SerializableModel):
    story = db.ReferenceProperty(Story, collection_name="documents")
    path = db.StringProperty()
    name = db.StringProperty()
    
    def get_document(self):
        import static
        return static.get(self.document_path)

