# Create your views here.
import sys
from django.http import HttpResponse
from django import forms
from displays.models import Customer
from django.template import Context, loader
import displays.schedule
import displays.home
import displays.html_utils


def home(request):
    return HttpResponse('This is the home of RCFKanban.')

class LoginForm(forms.Form):
    user_name = forms.CharField(max_length = 15)

def add_user_to_session(request, user_name, user_id):
    request.session['user_name'] = user_name
    request.session['user_id'] = user_id
    print >>sys.stderr, "SESSION USER", request.session['user_name']

def show_welcome_form(request, user_name):
    return displays.home.logged_in_page(request, user_name)

def has_user_name(request):
    if request.method == 'GET':
        params = request.GET
    else:
        params = request.POST
    if 'user_name' in params:
        return (True, params['user_name'])
    else:
        return (False, None)

def login_unknown(request, user_name):
    return show_login_form(request, error_text = 'User name is unknown')

def login_inactive(request, user_name):
    return show_login_form(request,
                           error_text = (
            'User is inactive.  Contact staff for reactivation'))
    

def login_good(request, user_name, user_id):
    add_user_to_session(request, user_name, user_id)
    return show_welcome_form(request, user_name)

def login_verify(request, user_name):
    users = Customer.objects.filter(name=user_name)
    print >>sys.stderr, "users", users, len(users)
    if len(users) == 0:
        print >>sys.stderr, "UNKNOWN"
        return login_unknown(request, user_name)
    elif users[0].is_active:
        print >>sys.stderr, "USER", users[0].is_active, users[0].id
        return login_good(request, user_name, users[0].id)
    else:
        return login_inactive(request, user_name)

def show_login_form(request, error_text = None):
    template = loader.get_template('displays/login.html')
    form = LoginForm()
    starter = displays.html_utils.kanban_context_dictionary()
    starter['HTML_TITLE'] = 'Kanban Login'
    starter['FORM'] = form
    if error_text is not None:
        starter['ERROR_TEXT'] = error_text
    context = Context(starter)
    return HttpResponse(template.render(context))

def login(request):
    print >>sys.stderr, "LOGIN"
    (has_name, user_name) = has_user_name(request)
    if has_name:
        return login_verify(request, user_name)
    else:
        return show_login_form(request)

def users(request):
    user_list = Customer.objects.order_by('name')
    user_text = ', '.join([u.name for u in user_list])
    template = loader.get_template('displays/index.html')
    starter = displays.html_utils.kanban_context_dictionary()
    starter['USERS'] = user_list
    context = Context(starter)
    return HttpResponse(template.render(context))

def logout(request):
    print >>sys.stderr, "LOGOUT"
    (has_name, user_name) = displays.login_utils.check_if_logged_in(request)
    print >>sys.stderr, "HAS", has_name
    if has_name:
        print >>sys.stderr, "HAS NAME"
        try:
            del request.session['user_name']
        except KeyError, ex:
            print >>sys.stderr, "EXCEPTION", ex
            # could get a KeyError if running multithreaded
            print >>sys.stderr, "NO USER NAME IN LOGOUT"
    return displays.home.home(request)
