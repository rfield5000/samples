"""
Tic Tac Toe driver program.

Utilize a table which, for each position,
gives a list of best moves.

Copyright 2009, Robert C. Field

"""
import sys
import os
import datetime
import cgi
import random

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

class CleanupPage(webapp.RequestHandler):

  def get(self):
    form = cgi.FieldStorage()
    path = os.path.join (os.path.dirname(__file__), 'cleanup.html')
    self.response.out.write(template.render(path, None))

  def post(self):
    self.get()

application = webapp.WSGIApplication(
  [
    ('/cleanup', CleanupPage),
    ],
  debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  #print >>sys.stderr, "MAIN CALLED"
  main()
