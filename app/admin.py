
import configuration

import appengine_admin

from google.appengine.ext import db, webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import models

urls = (
    (r'(/admin)(.*)$', appengine_admin.Admin),
)
application = webapp.WSGIApplication(urls, debug=configuration.DEBUG)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
