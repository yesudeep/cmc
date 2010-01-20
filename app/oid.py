#!/usr/bin/env python
# -*- coding: utf-8; mode: python; tab-width: 4; indent-tabs-mode: nil; -*-
# Temporary OpenID handlers.
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

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import memcache
from openid.extensions import sreg
from aeoid.handlers import BaseHandler
from aeoid import users, middleware
from gaefy.jinja2.code_loaders import FileSystemCodeLoader
from haggoo.template.jinja2 import render_generator

OPENID_LOGIN_PATH = '/_oid/login'
TWO_MINUTES_IN_SECONDS = 120

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

class RequestHandler(BaseHandler):
    def render_template(self, template_name, template_values):
        self.response.out.write(render_cached_template(template_name, **template_values))


class BeginLoginHandler(RequestHandler):
  def get(self):
    openid_url = self.request.get('openid_identifier')
    if not openid_url:
      self.render_template('login.html', {
          'login_url': OPENID_LOGIN_PATH,
          'continue': self.request.get('continue', '/')
      })
      return
 
    consumer = self.get_consumer()
    request = consumer.begin(openid_url)
    
    # TODO: Support custom specification of extensions
    # TODO: Don't ask for data we already have, perhaps?
    request.addExtension(sreg.SRegRequest(required=['nickname', 'email']))    
 
    continue_url = self.request.get('continue', '/')
    return_to = "%s%s?continue=%s" % (self.request.host_url,
                                      users.OPENID_FINISH_PATH, continue_url)
    self.redirect(request.redirectURL(self.request.host_url, return_to))
    self.session.save()
 
  def post(self):
    self.get()

urls = (
    # Pages.
    ('/_oid/login', BeginLoginHandler),
)
application = webapp.WSGIApplication(urls, debug=configuration.DEBUG)
application = middleware.AeoidMiddleware(application)

def main():
    from gaefy.db.datastore_cache import DatastoreCachingShim
    DatastoreCachingShim.Install()
    run_wsgi_app(application)
    DatastoreCachingShim.Uninstall()

if __name__ == "__main__":
    main()
