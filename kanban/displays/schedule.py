#
#
# Copyright 2014, Robert C. Field, All Rights Reserved
#
import sys
import datetime

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

import TimeStamp
import TicketStates
import ScheduleAssets

def make_table(display_items, max_length):
    #print >>sys.stderr, "TABLE", display_items, max_length
    result = '<table class="item_table" border="4" style="border-collapse:collapse;">\n'
    result += '<tr>\n'
    for item in TicketStates.display_states:
        result += ('<th>'+TicketStates.display_names[item] + '</th>')
    result += '\n<tr>\n'
    result += '<tr>\n'
    for item in TicketStates.display_states:
        result += '<td>'
        if len(display_items[item]) == 0:
            result += "&nbsp;"
        else:
            for one_item in display_items[item]:
                id_num = one_item['id']
                id_tag = 'id_tag_%d' % id_num
                result += (('<p class="item_text" id="%s" db_id="%s" db_state="%s"><span class="text_holder">'
                            % (id_tag, str(id_num), item))
                           + cgi.escape(one_item['string']).encode('ascii', 'xmlcharrefreplace')
                           + '</span></p>\n')
        result += '</td>\n'
                      
    result += '</tr>\n'
    result += '</table>\n'
    return result

                   

def generate_css_tags():
    return '<link rel="stylesheet" type="text/css" href="/kanban/css?target=kanban.css" />\n'

def generate_javascript_tags():
    result = ''
    for source in ('jquery.js', 'kanban.js'):
        result += ('<script type="text/javascript" src="/kanban/javascript?target=%s"></script>\n'
                   % source)
    return result

def generate_head_tags():
    return generate_css_tags() + generate_javascript_tags()

def task_create(request):
    (logged_in, user_name, user_id) = displays.login_utils.check_if_logged_in(request)
    print >>sys.stderr, "GET ", request.GET, "LOGGED", logged_in, "USER", user_name
    table_text = ''
    if logged_in:
        try:
            the_text = request.GET['new_text']
            the_text = the_text.replace("\n", " ")
            if (len(the_text) > 200):
                job_status = "TOO LONG"
            else:
                the_item = models.Task(text = the_text,
                                       state = "NEW",
                                       owner = models.Customer(id=user_id))
                the_item.save()
                job_status = "OK"
                table_text = make_item_table(request)
            js_result = json.dumps({'status':job_status,'table':table_text});
        except Exception, ex:
            js_result = json.dumps({'status':'ERROR ' + str(ex)});
    else:
        js_result = json.dumps({'status':'CREDENTIAL_FAILURE',});
    print >>sys.stderr, "RESULT", js_result
    return HttpResponse(js_result)

def task_update_work(request):
    the_id = request.GET['id']
    new_state = request.GET['choice']
    internal_state = None
    for (kk,vv) in TicketStates.display_names.items():
        print >>sys.stderr, kk, vv
        if vv.upper() == new_state.upper():
            internal_state = kk
            break
    if internal_state is None:
        if new_state.upper() == 'CLOSE':
            internal_state = 'CLOSED'
    print >>sys.stderr, "INTERNAL", internal_state, "NEW", new_state
    if internal_state is not None:
        changed_tasks = Task.objects.filter(id=the_id).update(state = internal_state,
                                                              changed=datetime.datetime.now())
        #print >>sys.stderr, "CHANGED %d ROWS FOR PARAM |%s|" % (changed_tasks, the_id)
        #print >>sys.stderr, "DONE CHANGED %d ROWS FOR PARAM |%s|" % (changed_tasks, the_id)
        resp_string = 'OK'
    else:
        resp_string = 'OOPS'
    return resp_string

def task_update(request):
    (logged_in, user_name, user_id) = displays.login_utils.check_if_logged_in(request)
    have_keys = (('id' in request.GET)
                 and ('choice' in request.GET))
    if have_keys:
        resp_string = task_update_work(request)
    else:
        print >>sys.stderr, "BAD"
        resp_string = 'BAD'
    js_result = json.dumps({'status':resp_string,
                            'table':make_item_table(request)})
    return HttpResponse(js_result)

def get_task_list(request):
    return HttpResponse("<h1>Ruh-Roh</h1>")

def _get_display_items(user_name):
    cursor = connection.cursor()
    cursor.execute(('SELECT * FROM displays_task, displays_customer'
                    + ' WHERE displays_task.owner_id = displays_customer.id'
                    + ' AND displays_customer.name = \'%s\''
                    + 'ORDER BY displays_task.state, displays_task.created')
                   % user_name)
    max_length = -1
    results = []
    by_states = {}
    for one_state in TicketStates.display_states:
        by_states[one_state] = []
    for row in cursor.fetchall():
        #print >>sys.stderr, "ROW", str(row)
        task_id = row[0]
        task_string = row[1]
        task_state = row[2]
        
        is_shown = task_state in TicketStates.display_states
        item_hash = {}
        item_hash['id'] = task_id
        item_hash['string'] = task_string
        item_hash['state'] = task_state
        
        if is_shown:
            by_states[task_state].append(item_hash)
            results.append([task_id, task_string, task_state, item_hash])
            max_length = max(max_length,len(by_states[task_state]))
    #print >>sys.stderr, "STATES", str(by_states), "MAX", max_length
    return (results, by_states, max_length)
                         

def make_item_table(request):
    (logged_in, user_name, user_id) = displays.login_utils.check_if_logged_in(request)
    (showable, by_states, max_column_length) = _get_display_items(user_name)
    if (logged_in):
        (showable, by_states, max_column_length) = _get_display_items(user_name)
        #print >>sys.stderr, "SHOWABLE", str(showable)
        result = make_table(by_states, max_column_length)
        #print >>sys.stderr, "\n\n", str(result)
        return result
    else:
        return ''

def return_item_table(request):
    (logged_in, user_name, user_id) = displays.login_utils.check_if_logged_in(request)
    js_result = json.dumps({'status':'OK',
                            'table':make_item_table(request)})
    return HttpResult(js_result)

def page_for_logged_in(request, user_name, user_id):
    login_message = 'LOG IN: ' + user_name
    counter = ''
    starter = displays.html_utils.kanban_context_dictionary()
    starter['IS_LOGGED_IN'] = 1
    starter['TABLE_TEXT'] = make_item_table(request)
    template = loader.get_template(ScheduleAssets.schedule_template_path) ###'displays/schedule.html')
    starter['DOC_TEXT'] = ''
    starter['LOGIN'] = login_message
    starter['APPNAME'] = "RCF Kanban Board"
    starter['TIMESTAMP'] = "As of %s" % (TimeStamp.timestamp(),)
    use_jquery = True
    starter['STYLES_CSS_SCRIPTS'] = generate_head_tags()
    context = Context(starter)

    return HttpResponse(template.render(context))

def page_for_not_logged_in(request):
    login_message = 'LOG IN: ' + 'NOT LOGGED IN'
    counter = ''
    starter = displays.html_utils.kanban_context_dictionary()
    starter['TABLE_TEXT'] = ''

    template = loader.get_template(ScheduleAssets.schedule_template_path) ###'displays/schedule.html')
    starter['DOC_TEXT'] = ''
    starter['LOGIN'] = login_message
    starter['APPNAME'] = "RCF Kanban Board"
    starter['TIMESTAMP'] = "As of %s" % (TimeStamp.timestamp(),)
    use_jquery = True
    starter['STYLES_CSS_SCRIPTS'] = generate_head_tags()
    context = Context(starter)

    return HttpResponse(template.render(context))

def make_schedule(request):
    """
    Build the schedule page.

    Determine if logged in, and user id when actually logged in.

    Render the page.  In particular, invoke make_item_table() to
    create the table of open items.

    """
    (logged_in, user_name, user_id) = displays.login_utils.check_if_logged_in(request)
    if logged_in:
        return page_for_logged_in(request, user_name, user_id)
    else:
        return page_for_not_logged_in(request)
