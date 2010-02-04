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

from google.appengine.ext import db, webapp
from google.appengine.api import memcache
from google.appengine.ext.webapp.util import run_wsgi_app
from gaefy.jinja2.code_loaders import FileSystemCodeLoader
from haggoo.template.jinja2 import render_generator
from haggoo.template.jinja2.filters import datetimeformat
from aeoid import users, middleware
import logging
import search
from models import Story
from facebook.webappfb import FacebookCanvasHandler, FacebookRequestHandler

# Hack
users.OPENID_LOGIN_PATH = '/_oid/login'

# Set up logging.
logging.basicConfig(level=logging.DEBUG)

TWO_MINUTES_IN_SECONDS = 60 * 2


URL_PATTERN_SUFFIX = '/?'
ROOT_URL = '/'
URL_LIST = (
    'contact',
    'privacy',
    'tos',
    'author',
    'chaiwala',
    'story',
    'about',
    'celebrity',
    'title',
    'release',
    'goodies',
)
APP_URLS = {
    'index': ROOT_URL,
    'indexing': ROOT_URL + 'tasks/searchindexing',
}
APP_URL_PATTERNS = {
    'index': ROOT_URL,
    'indexing': ROOT_URL + 'tasks/searchindexing' + URL_PATTERN_SUFFIX,
}
for u in URL_LIST:
    APP_URLS[u] = ROOT_URL + u
for u in URL_LIST:
    APP_URL_PATTERNS[u] = ROOT_URL + u + URL_PATTERN_SUFFIX

POLAROID_URL_LIST = (
    'image/download/home',
    'image/download/tell_me_your_story',
    'image/download/what_and_why',
    'image/download/about_the_author'
)

template_builtins = {
    'app_urls': APP_URLS,
}
template_builtins.update(configuration.TEMPLATE_BUILTINS)
render_template = render_generator(loader=FileSystemCodeLoader, builtins=template_builtins, filters={
    'datetimeformat': datetimeformat,
    })

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

class LoginHandler(RequestHandler):
    def get(self):
        pass

def with_story(fun):
    def decorate(self, entity_id=None):
        entity = None
        if entity_id:
            entity = Story.get_by_id(int(entity_id))
            if not entity:
                self.error(404)
            return
        fun(self, entity)
    return decorate

class StoryEditHandler(StaticRequestHandler):
    def get(self, id):
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
            return
        logging.warn("Logged in as %s (%s)", user.nickname(), user.user_id())
        self.render_to_response("story_edit.html", 
            story=Story.get_by_id(int(id, 10)),
            request_too_large_error=False)


    def post(self, id):
        import os, static, hashlib
        from models import StoryAuthor, Story, StoryDocument
        from django.template.defaultfilters import slugify
        from google.appengine.runtime.apiproxy_errors import RequestTooLargeError
        
        content = self.request.get('content')
        title = self.request.get('title')
        
        story = Story.get_by_id(int(id, 10))
        story.content = content
        story.title = title
        story.put()

        try:
            request_document = self.request.get('document')
            document_file = self.request.POST['document']        
            if request_document:
                document_body = document_file.value
                document_digest = hashlib.sha1(document_body).hexdigest()
                split_name = os.path.splitext(os.path.basename(document_file.filename))
                filename = slugify(split_name[0]) or document_digest
                document_name = filename + split_name[1]
        
                document_path = '/story/%d/document/%s/%s' % (story.key().id(), document_digest, document_name)
                logging.info(document_path)
                story_document = StoryDocument(story=story, path=document_path, name=document_name)
                story_document.put()
                document = static.set(document_path, document_body, document_file.type)
            self.get(id)                
        except RequestTooLargeError, message:
            self.render_to_response("story_edit.html", 
                story=Story.get_by_id(int(id, 10)),
                request_too_large_error=True)

class AboutStoryHandler(StaticRequestHandler):
    def get(self):
        self.render_to_response('about_story.html')

class StoryHandler(StaticRequestHandler):
    def get(self):
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
            return
        logging.info("User: nickname: %s, email: %s", user.nickname(), user.email())
        from api_preferences import facebook as fb_prefs, google_friend_connect as gfc
        self.render_to_response("start.html",
                                   FACEBOOK_API_KEY=fb_prefs.get('api_key'),
                                   FACEBOOK_CROSS_DOMAIN_RECEIVER_URL=fb_prefs.get('cross_domain_receiver_url'),
                                   GOOGLE_FRIEND_CONNECT_SITE_ID=gfc.get('site_id'),
                                   request_too_large_error=False,
                                   logout_url=users.create_logout_url(self.request.uri),
                                   email=user.email(),
                                   nickname=user.nickname())
    
    def post(self):
        import os, static, hashlib
        from models import StoryAuthor, Story, StoryDocument
        from django.template.defaultfilters import slugify
        from google.appengine.runtime.apiproxy_errors import RequestTooLargeError
        
        title = self.request.get('title')
        content = self.request.get('content')
        full_name = self.request.get('full_name')
        mobile_number = self.request.get('mobile_number')
        email = self.request.get('email')

        author = StoryAuthor(full_name=full_name, email=email, mobile_number=mobile_number)
        author.put()
    
        story = Story(title=title)
        if content:
            story.content = content
        story.author = author
        story.put()

        try:
            request_document = self.request.get('document')
            if request_document:
                document_file = self.request.POST['document']        
                document_body = document_file.value
                document_digest = hashlib.sha1(document_body).hexdigest()
                split_name = os.path.splitext(os.path.basename(document_file.filename))
                filename = slugify(split_name[0]) or document_digest
                document_name = filename + split_name[1]
        
                document_path = '/story/%d/document/%s/%s' % (story.key().id(), document_digest, document_name)
                logging.info(document_path)
                story_document = StoryDocument(story=story, path=document_path, name=document_name)
                story_document.put()
                document = static.set(document_path, document_body, document_file.type, name=document_name)
                self.render_to_response("thanks/story.html", document=story_document, story=story)
            else:
                self.render_to_response("thanks/story.html", story=story)
                
        except RequestTooLargeError, message:
            from api_preferences import facebook as fb_prefs, google_friend_connect as gfc
            self.render_to_response("start.html",
                                       FACEBOOK_API_KEY=fb_prefs.get('api_key'),
                                       FACEBOOK_CROSS_DOMAIN_RECEIVER_URL=fb_prefs.get('cross_domain_receiver_url'),
                                       GOOGLE_FRIEND_CONNECT_SITE_ID=gfc.get('site_id'),
                                       request_too_large_error=True,
                                       title=title,
                                       content=content,
                                       full_name=full_name,
                                       email=email,
                                       mobile_number=mobile_number)

class AboutHandler(StaticRequestHandler):
    """Handler for the what and why page."""
    def get(self):
        self.render_to_response('what.html')

class CelebrityHandler(StaticRequestHandler):
    def get(self):
        self.render_to_response('celebrity.html')

    def post(self):
        from models import Celebrity
        name = self.request.get('name')
        celebrity = Celebrity.up_vote_or_insert(name=name)
        self.get()
        

class SuggestTitleHandler(StaticRequestHandler):
    def get(self):
        self.render_to_response('suggest_title.html')
    
    def post(self):
        from models import SuggestedTitle, SuggestedTitlePerson
        title = self.request.get('title')
        full_name = self.request.get('full_name')
        mobile_number = self.request.get('mobile_number')
        email = self.request.get('email')
        register_for_book = self.request.get('register_for_book')
        
        to_be_saved = []
        if register_for_book and register_for_book == 'yes':
            from models import NotifyReleasePerson
            person = NotifyReleasePerson(full_name=full_name, email=email, mobile_number=mobile_number)
            to_be_saved.append(person)

        suggested_title = SuggestedTitle.up_vote_or_insert(title=title)        
        person = SuggestedTitlePerson(full_name=full_name, email=email, mobile_number=mobile_number)
        person.suggested_title = suggested_title
        to_be_saved.append(person)
        db.put(to_be_saved)
        self.render_to_response('thanks/suggested_title.html')

class TitleVoteHandler(StaticRequestHandler):
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
    
    def post(self):
        from models import NotifyReleasePerson
        full_name = self.request.get('full_name')
        mobile_number = self.request.get('mobile_number')
        email = self.request.get('email')
        
        person = NotifyReleasePerson(full_name=full_name, email=email, mobile_number=mobile_number)
        person.put()
        self.render_to_response("thanks/notify_release.html")
    
class GoodiesHandler(StaticRequestHandler):
    def get(self):
        self.render_to_response('goodies.html', polaroid_urls=POLAROID_URL_LIST)
        
class CelebrityListHandler(StaticRequestHandler):
    def get(self):
        from django.utils import simplejson as json
        from models import Celebrity
        from jsmin import jsmin
        celebrities = Celebrity.get_latest()
        celebrities_list = [dict(tag=c.slug, count=c.vote_count) for c in celebrities]
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(jsmin(json.dumps(celebrities_list)))

class OldFacebookAppHandler(FacebookCanvasHandler):
    def canvas(self):
        #from api_preferences import facebook_app as fb_app
        #import facebook
        #self.facebookapi = facebook.Facebook(fb_app.get('api_key'), fb_app.get('application_secret'))
        friends_ids = self.facebook.friends.get()
        logging.info(friends_ids)
        friends = self.facebook.users.getInfo(friends_ids, ['name', 'uid', 'pic'])
        logging.info(friends)
        rendered_response = render_template("social/facebook.fbml", 
            uid=self.facebook.uid, 
            friends=friends, 
            friends_ids=friends_ids, 
            canvas_url=configuration.FACEBOOK_CANVAS_URL)
        self.response.out.write(rendered_response)

class FacebookAppHandler(FacebookRequestHandler):
    def get(self):
        from api_preferences import facebook_app
        from cgi import escape
        name_fbml = """<fb:serverfbml>
                <script type=text/fbml>
                <fb:fbml>
                    <fb:name linked=false useyou=false firstnameonly=false />
                </fb:fbml>
                </script>
                </fb:serverfbml>"""
        
        response = render_template("facebook_app.html", 
            name_fbml=name_fbml, 
            facebook_config=facebook_app)
        self.response.out.write(response)

# URL-to-request-handler mappings.
urls = (
    # Pages.
    (APP_URL_PATTERNS['index'], IndexHandler),
    (APP_URL_PATTERNS['contact'], ContactHandler),
    (APP_URL_PATTERNS['privacy'], PrivacyHandler),
    (APP_URL_PATTERNS['tos'], TermsOfUseHandler),
    (APP_URL_PATTERNS['author'], ChaiwalaHandler),
    (APP_URL_PATTERNS['chaiwala'], ChaiwalaHandler),
    (APP_URL_PATTERNS['story'], AboutStoryHandler),
    (APP_URL_PATTERNS['about'], AboutHandler),
    (APP_URL_PATTERNS['celebrity'], CelebrityHandler),
    (APP_URL_PATTERNS['title'], SuggestTitleHandler),
    (APP_URL_PATTERNS['release'], BookReleaseHandler),
    (APP_URL_PATTERNS['goodies'], GoodiesHandler),
    
    ('/celebrity/list', CelebrityListHandler),
    ('/story/(\d+)/?', StoryEditHandler),
    ('/story/new/?', StoryHandler),

    # Facebook handlers.
    ('/social/facebook/?', FacebookAppHandler),
    #('/facebook/post-auth/?', FacebookPostAuthorizeHandler),
    #('/facebook/post-remove/?', FacebookPostRemoveHandler),

    # Search and indexing.
    (APP_URL_PATTERNS['indexing'], search.SearchIndexing),
)
application = webapp.WSGIApplication(urls, debug=configuration.DEBUG)
application = middleware.AeoidMiddleware(application)

# Web application entry-point.
def main():
    from gaefy.db.datastore_cache import DatastoreCachingShim
    DatastoreCachingShim.Install()
    run_wsgi_app(application)
    DatastoreCachingShim.Uninstall()

if __name__ == '__main__':
    main()
