# Views for testig template includes
import sys
from django.http import HttpResponse, HttpResponseNotFound
from django.db import connection, transaction
from displays.models import Customer, Task
from django.template import Context, loader
import django.utils.html
import displays.html_utils
import displays.login_utils


def include(request):
    template = loader.get_template('displays/include_extend.html')
    starter = displays.html_utils.kanban_context_dictionary()
    context = Context(starter)
    context['FIRST'] = 'FIRST TEXT'
    context['SECOND'] = 'SECOND TEXT'
    context['INCLUDED'] = 'INCLUDED TEXT'
    return HttpResponse(template.render(context))
