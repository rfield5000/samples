from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    # Examples
    url(r'^$', 'displays.home.home', name='home'),
    url(r'^kanban/$', 'displays.home.home', name='application'),
    url(r'^kanban/include$', 'displays.include.include', name='application'),
    url(r'^kanban/login$', 'displays.views.login', name='application'),
    url(r'^kanban/logout$', 'displays.views.logout', name='application'),
    url(r'^kanban/schedule/?$', 'displays.schedule.make_schedule', name='application'),
    url(r'^kanban/javascript/?$', 'displays.javascript.serve_javascript', name='application'),
    url(r'^kanban/css/', 'displays.css.serve_css', name='application'),
    url(r'^kanban/get_task_list/?$', 'displays.schedule.get_task_list', name='application'),
    url(r'^kanban/task_update', 'displays.schedule.task_update', name='application'),
    url(r'^kanban/task_create', 'displays.schedule.task_create', name='application'),
    url(r'^kanban/css_demo', 'displays.demo.css', name='application'),
    url(r'^kanban/users$', 'displays.views.users', name='application'),
    
    # Uncomment the admin/doc line below to enable admin documentation
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    
    # Uncomment the next line to enable the admin
    url(r'^admin/', include(admin.site.urls)),
)
