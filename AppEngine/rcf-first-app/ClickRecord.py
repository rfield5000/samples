"""
Keep track of visitor data.

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

class ClickRecord(db.Model):
  refer = db.StringProperty()
  now = db.DateTimeProperty(auto_now_add = True)
