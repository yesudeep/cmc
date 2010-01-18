#!/usr/bin/env python
# -*- coding: utf-8; mode: python; tab-width: 4; indent-tabs-mode: nil; -*-
# Main handlers.
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
from gaefy.db.datastore_cache import DatastoreCachingShim
from google.appengine.ext import db, webapp
from google.appengine.api import memcache
from google.appengine.ext.webapp.util import run_wsgi_app
from gaefy.jinja2.code_loaders import FileSystemCodeLoader
from haggoo.template.jinja2 import render_generator
from haggoo.sessions import SessionRequestHandler
import logging
import search

# Set up logging.
logging.basicConfig(level=logging.DEBUG)

TWO_MINUTES_IN_SECONDS = 60 * 2

INDEXING_URL = '/tasks/searchindexing'

POLAROID_URL_LIST = (
    'image/download/home',
    'image/download/tell_me_your_story',
    'image/download/what_and_why',
    'image/download/about_the_author'
)

render_template = render_generator(loader=FileSystemCodeLoader, builtins=configuration.TEMPLATE_BUILTINS)



def render_cached_template(template_name, **kwargs):
    cache_key = template_name + str(kwargs)
    response = memcache.get(cache_key)
    if not response:
        response = render_template(template_name, **kwargs)
        memcache.set(cache_key, response, TWO_MINUTES_IN_SECONDS)
    return response

if configuration.DEPLOYMENT_MODE == configuration.MODE_DEVELOPMENT:
    render_cached_template = render_template

class RequestHandler(webapp.RequestHandler):
    def render_to_response(self, template_name, **template_values):
        self.response.out.write(render_template(template_name, **template_values))
        
class StaticRequestHandler(RequestHandler):
    def render_to_response(self, template_name, **template_values):
        self.response.out.write(render_cached_template(template_name, **template_values))

# Handlers
class IndexHandler(StaticRequestHandler):
    def get(self):
        self.render_to_response('index.html')

class PrivacyHandler(StaticRequestHandler):
    def get(self):
        self.render_to_response('privacy.html')

class ContactHandler(StaticRequestHandler):
    def get(self):
        self.render_to_response('contact.html')

class TermsOfUseHandler(StaticRequestHandler):
    def get(self):
        self.render_to_response('terms_of_use.html')

class ChaiwalaHandler(StaticRequestHandler):
    def get(self):
        self.render_to_response('chaiwala.html')
        
class StoryHandler(StaticRequestHandler):
    def get(self):
        from api_preferences import facebook as fb_prefs, google_friend_connect as gfc
        self.render_to_response("start.html",
                                   FACEBOOK_API_KEY=fb_prefs.get('api_key'),
                                   FACEBOOK_CROSS_DOMAIN_RECEIVER_URL=fb_prefs.get('cross_domain_receiver_url'),
                                   GOOGLE_FRIEND_CONNECT_SITE_ID=gfc.get('site_id'))


class WhatHandler(StaticRequestHandler):
    """Handler for the what and why page."""
    def get(self):
        self.render_to_response('what.html')

class CelebrityHandler(StaticRequestHandler):
    def get(self):
        self.render_to_response('vote.html')

class FacebookPostAuthorizeHandler(SessionRequestHandler):
    def post(self):
        logging.info(self.request)
        pass

class FacebookPostRemoveHandler(SessionRequestHandler):
    def post(self):
        logging.info(self.request)
        pass

class SuggestTitleHandler(StaticRequestHandler):
    def get(self):
        self.render_to_response('suggest_title.html')
        

class TitleVoteHandler(SessionRequestHandler):
    def get(self, vote):
        if vote == 'yes':
            response = render_cached_template("thanks/suggested_title.html")
        else:
            response = render_cached_template("suggest_title.html")
        self.response.out.write(response)

    def post(self, vote):
        if vote == 'yes':
            pass
        elif vote == 'no':
            suggested_title = self.request.get('suggested_title')
            
class BookReleaseHandler(StaticRequestHandler):
    def get(self):
        self.render_to_response('release.html')
        
class GoodiesHandler(StaticRequestHandler):
    def get(self):
        self.render_to_response('goodies.html', polaroid_urls=POLAROID_URL_LIST)
        
# URL-to-request-handler mappings.
urls = (
    # Pages.
    ('/', IndexHandler),
    ('/contact/?', ContactHandler),
    ('/privacy/?', PrivacyHandler),
    ('/tos/?', TermsOfUseHandler),
    ('/chaiwala/?', ChaiwalaHandler),
    ('/story/?', StoryHandler),
    ('/what/?', WhatHandler),
    ('/celebrity/?', CelebrityHandler),
    ('/title/?', SuggestTitleHandler),
    ('/release/?', BookReleaseHandler),
    ('/goodies/?', GoodiesHandler),

    # Facebook handlers.
    ('/facebook/post-auth/?', FacebookPostAuthorizeHandler),
    ('/facebook/post-remove/?', FacebookPostRemoveHandler),

    # Search and indexing.
    (INDEXING_URL, search.SearchIndexing),
)
application = webapp.WSGIApplication(urls, debug=configuration.DEBUG)

# Web application entry-point.
def main():
    DatastoreCachingShim.Install()
    run_wsgi_app(application)
    DatastoreCachingShim.Uninstall()

if __name__ == '__main__':
    main()
