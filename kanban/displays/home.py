# Views for displaying schedules
import sys
from django.http import HttpResponse
from django.db import connection, transaction
from displays.models import Customer, Task
from django.template import Context, loader
import django.utils.html
import displays.html_utils
import displays.login_utils

def not_logged_in_page(request):
    template = loader.get_template('displays/home.html')
    starter = displays.html_utils.kanban_context_dictionary()
    context = Context(starter)
    context['SHOW_LOGIN'] = '1'
    context['LOGIN_URL'] = '/kanban/' + 'login';
    print >>sys.stderr, "URL", context['LOGIN_URL']
    context['DISPLAY_URL'] = '/kanban/' + 'schedule';
    return HttpResponse(template.render(context))

def logged_in_page(request, user_name):
    template = loader.get_template('displays/home.html')
    starter = displays.html_utils.kanban_context_dictionary()
    context = Context(starter)
    context['SHOW_USER'] = '1'
    context['USER_NAME'] = user_name
    context['DISPLAY_URL'] = '/kanban/' + 'schedule';
    context['LOGOUT_URL'] = '/kanban/' + 'logout';
    return HttpResponse(template.render(context))

def home(request):
    print >>sys.stderr, request.path
    print >>sys.stderr, (request.path_info, request.method, request.COOKIES,
                         request.session,
                         request.session.get('is_important', False))
    if request.method == 'GET':
        params = request.GET
    else:
        params = request.POST
    print >>sys.stderr, "params", params
    (logged_in, user_name, user_id) = displays.login_utils.check_if_logged_in(request)
    if (logged_in):
        print >>sys.stderr, "GOT A NAME"
        return logged_in_page(request, user_name)
    else:
        print >>sys.stderr, "NOT LOGGED IN"
        return not_logged_in_page(request)

    template = loader.get_template('displays/home.html')
    starter = displays.html_utils.kanban_context_dictionary()
    context = Context(starter)
    context['LOGIN_URL'] = request.path + 'login';
    context['DISPLAY_URL'] = '/kanban/' + 'schedule';
    return HttpResponse(template.render(context))
