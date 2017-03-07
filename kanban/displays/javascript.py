#
#
# Copyright 2014, Robert C. Field, All Rights Reserved
#
import sys
import datetime

# Views for displaying schedules
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect, HttpResponseBadRequest
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

import TimeStamp
import TicketStates
import ScheduleAssets

def serve_javascript(request):
    if 'target' in request.REQUEST:
        return HttpResponseRedirect("/static/" + request.REQUEST['target']);
    else:
        return HttpResponseBadRequest()

