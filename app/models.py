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
from dbhelper import SerializableModel, serialize_entities, deserialize_entities
import appengine_admin
import static

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

    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.__unicode__()


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
        
    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name



class Person(SerializableModel):
    full_name = db.StringProperty(required=True)
    email = db.EmailProperty(required=True)
    mobile_number = db.StringProperty()

    def __unicode__(self):
        return self.full_name
    
    def __str__(self):
        return self.full_name


class SuggestedTitlePerson(Person):
    suggested_title = db.ReferenceProperty(SuggestedTitle, collection_name='people')

    def __unicode__(self):
        return self.full_name
    
    def __str__(self):
        return self.full_name

class StoryAuthor(Person):
    def __unicode__(self):
        return self.full_name
    
    def __str__(self):
        return self.full_name


class NotifyReleasePerson(Person):
    def __unicode__(self):
        return self.full_name
    
    def __str__(self):
        return self.full_name

class Story(SerializableModel):
    title = db.StringProperty(required=True)
    content = db.TextProperty(default=db.Blob(""))
    author = db.ReferenceProperty(StoryAuthor, collection_name="stories")

    def __unicode__(self):
        return self.title
    
    def __str__(self):
        return self.title

    
    def get_latest_document(self):
        """Returns the latest document submitted."""
        pass

class StoryDocument(SerializableModel):
    story = db.ReferenceProperty(Story, collection_name="documents")
    path = db.StringProperty()
    name = db.StringProperty()
    
    def __unicode__(self):
        return self.name
    
    def __str__(self):
        return self.name
    
    def get_document(self):
        import static
        return static.get(self.document_path)

class AdminCelebrity(appengine_admin.ModelAdmin):
    model = Celebrity
    listFields = ("name", "slug", "vote_count")
    editFields = ("name",)
    readonlyFields = ("slug", "when_created", 'vote_count', "when_modified")
    listGql = "order by name asc"
    
class AdminStoryAuthor(appengine_admin.ModelAdmin):
    model = StoryAuthor
    listFields = ("full_name", 'email', 'mobile_number',)
    editFields = ("full_name", "email", 'mobile_number',)
    listGql = 'order by full_name asc'

class AdminNotifyReleasePerson(appengine_admin.ModelAdmin):
    model = NotifyReleasePerson
    listFields = ("full_name", "email", "mobile_number",)
    editFields = ("full_name", "email", "mobile_number",)
    listGql = 'order by full_name asc'
    
class AdminSuggestedTitlePerson(appengine_admin.ModelAdmin):
    model = SuggestedTitlePerson
    listFields = ("full_name", "email", "mobile_number", "suggested_title")
    editFields = ("full_name", "email", "mobile_number", "suggested_title")
    listGql = 'order by full_name asc'

class AdminSuggestedTitle(appengine_admin.ModelAdmin):
    model = SuggestedTitle
    listFields = ('title', 'people', 'vote_count')
    editFields = ('title', )
    readonlyFields = ('slug', 'people', 'vote_count', 'when_created', 'when_modified')

class AdminStory(appengine_admin.ModelAdmin):
    model = Story
    listFields = ('title', 'author')
    editFields = ('title', 'content')
    readonlyFields = ('author', 'when_created', 'when_modified')
    listGql = 'order by when_created desc'

class AdminStaticContent(appengine_admin.ModelAdmin):
    model = static.StaticContent
    listFields = ('body', 'content_type', 'status', 'last_modified')
    editFields = ()
    readonlyFields = ('body', 'content_type', 'status', 'last_modified', 'headers', 'etag')
    listGql = 'order by when_created desc'

appengine_admin.register(
    AdminStory,
    AdminCelebrity,
    AdminStoryAuthor,
    AdminNotifyReleasePerson,
    AdminSuggestedTitlePerson,
    AdminSuggestedTitle,
    AdminStaticContent
    )
