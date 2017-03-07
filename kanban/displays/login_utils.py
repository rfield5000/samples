# Create your views here.
import sys
from django.http import HttpResponse
from displays.models import Customer
from django.template import Context, loader

def user_property_name():
    return "user_name"

def id_property_name():
    return "user_id"

def check_if_logged_in(request):
    print >>sys.stderr, "check if logged in"
    the_name = request.session.get(user_property_name(), None)
    the_id = request.session.get(id_property_name(), None)
    print >>sys.stderr, "NAME", the_name, "ID", the_id
    return ((the_name is not None), the_name, the_id)
