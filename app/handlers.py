#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
import logging

# Set up logging.
logging.basicConfig(level=logging.DEBUG)

render_template = render_generator(loader=FileSystemCodeLoader, builtins=configuration.TEMPLATE_BUILTINS)

# Handlers
class IndexHandler(webapp.RequestHandler):
    """Handles the home page requests."""
    def get(self):
        response = render_template('index.html')
        self.response.out.write(response)

class PrivacyHandler(webapp.RequestHandler):
    """Handler for the privacy page."""
    def get(self):
        response = render_template('privacy.html')
        self.response.out.write(response)

class ContactHandler(webapp.RequestHandler):
    """Handler for the contacts page."""
    def get(self):
        response = render_template("contact.html")
        self.response.out.write(response)

class TermsOfUseHandler(webapp.RequestHandler):
    """Handler for the terms of use page."""
    def get(self):
        response = render_template('terms_of_use.html')
        self.response.out.write(response)

class ChaiwalaHandler(webapp.RequestHandler):
    """Handler for the chaiwala page."""
    def get(self):
        response = render_template('chaiwala.html')
        self.response.out.write(response)

class StartHandler(webapp.RequestHandler):
    """Handler for the getting started wizard."""
    def get(self):
        response = render_template("start.html")
        self.response.out.write(response)

class WhatHandler(webapp.RequestHandler):
    """"Handler for the why and what page."""
    def get(self):
        response = render_template("what.html")
        self.response.out.write(response)

# URL-to-request-handler mappings.
urls = (
    ('/', IndexHandler),
    ('/contact/?', ContactHandler),
    ('/privacy/?', PrivacyHandler),
    ('/tos/?', TermsOfUseHandler),
    ('/chaiwala/?', ChaiwalaHandler),
    ('/start/?', StartHandler),
    ('/what/?', WhatHandler),
)

# Web application entry-point.
def main():
    application = webapp.WSGIApplication(urls, debug=configuration.DEBUG)
    DatastoreCachingShim.Install()
    run_wsgi_app(application)
    DatastoreCachingShim.Uninstall()

if __name__ == '__main__':
    main()
