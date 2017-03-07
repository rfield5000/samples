# Create your views here.
from django.http import HttpResponse
from displays.models import Customer
from django.template import Context, loader


def html_strict_definition():
    return '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
   "http://www.w3.org/TR/html4/strict.dtd">'''

def kanban_context_dictionary():
    standard = {
        'HTML_DEF':html_strict_definition(),
        }
    return standard
