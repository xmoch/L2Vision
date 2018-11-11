#
# urls.py
# by zdev
#
# Handles URL dispatching
#
#------------------------------------------------------------------------------

from django.conf.urls.defaults import *

urlpatterns = patterns('l2v.views',

    (r'^$', 'index'),
    (r'^view/(?P<name>.+)$', 'view'),
    (r'^world_map/(?P<name>.+)$', 'world_map'),
    (r'^loot/(?P<name>.+)$', 'loot'),
    (r'^mobs/(?P<name>.+)$', 'mobs'),
    (r'^visitors/(?P<name>.+)$', 'visitors'),
    (r'^chat/(?P<name>.+)$', 'chat'),
    (r'^graphs/(?P<name>.+)$', 'graphs'),
    (r'^reset$', 'reset_all'),
    (r'^reset/(?P<name>.+)$', 'reset'),

)
