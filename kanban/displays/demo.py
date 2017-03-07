#
#
# Copyright 2014, Robert C. Field, All Rights Reserved
#
import sys
import datetime
import os

# Views for displaying schedules
from django.http import HttpResponse, HttpResponseNotFound
from django.db import connection, transaction
from displays.models import Customer, Task
from django.template import Context, loader
import django.utils.html
import displays.html_utils
import displays.login_utils
import cgi
import time
import json

import models

def css(request):
    """
    Build a CSS demo page

    """
    starter = displays.html_utils.kanban_context_dictionary()
    # Relating to templating
    template_directory = "displays"
    css_template_name = "css_demo.html"
    css_template_path = os.path.join(template_directory, css_template_name)
    template = loader.get_template(css_template_path)
    context = Context(starter)

    return HttpResponse(template.render(context))


