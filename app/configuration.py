#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Application configuration.
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

import sys
import os
import logging

from os.path import dirname, abspath, realpath, join as path_join

DIR_PATH = abspath(dirname(realpath(__file__)))
EXTRA_LIB_PATH = [
    path_join(DIR_PATH, 'appengine'),
    path_join(DIR_PATH, 'gaeutilities'),
    path_join(DIR_PATH, 'jinja2'),
    dirname(DIR_PATH),
]
sys.path = EXTRA_LIB_PATH + sys.path

logging.basicConfig(level=logging.INFO)


def sanitize_url(url):
    """Ensures that the URL ends with a slash."""
    if not url.endswith('/'):
        url = url + '/'
    return url


MODE_DEVELOPMENT = 'development'
MODE_PRODUCTION = 'production'
APPLICATION_ID = os.environ['APPLICATION_ID']
SERVER_PORT = os.environ['SERVER_PORT']
SERVER_NAME = os.environ['SERVER_NAME']
SERVER_SOFTWARE = os.environ['SERVER_SOFTWARE']

if SERVER_PORT and SERVER_PORT != '80':
    # We are using the development server.
    DEPLOYMENT_MODE = MODE_DEVELOPMENT
    HOST_NAME = '%s:%s' % (SERVER_NAME, SERVER_PORT,)
    LOCAL = True
    DEBUG = True
    MEDIA_URL = 'http://%s/s' % (HOST_NAME, )
else:
    # We are using the production server.
    DEPLOYMENT_MODE = MODE_PRODUCTION
    HOST_NAME = SERVER_NAME
    LOCAL = False
    DEBUG = False
    MEDIA_URL = 'http://'

if DEBUG:
    # Minification suffixex to use for CSS and JS files.
    CSS_MINIFIED = ''
    JS_MINIFIED = ''
else:
    CSS_MINIFIED = '-min'
    JS_MINIFIED = '-min'

# The URL root of the Website.
# For example: 
#     http://www.example.com/
#     http://localhost:8000/
ROOT_URL = 'http://%s/' % (HOST_NAME,)

# The builtin variables that are available to all templates.
TEMPLATE_BUILTINS = {
    'MEDIA_URL': sanitize_url(MEDIA_URL),
    'ROOT_URL': sanitize_url(ROOT_URL),
    'TEMPLATE_DEBUG': DEBUG,
    'CSS_MINIFIED': CSS_MINIFIED,
    'JS_MINIFIED': JS_MINIFIED,
    'LOCAL': LOCAL,
    'DEBUG': DEBUG,
    'DEPLOYMENT_MODE': DEPLOYMENT_MODE,
}

# Directories in which to search for templates.
TEMPLATE_DIRS = (
    path_join(DIR_PATH, 'templates'),
)
