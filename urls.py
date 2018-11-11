from django.conf.urls.defaults import *
import os

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (r"static/(?P<path>.*)/$", 'django.views.static.serve', {
       'document_root': "%s/data" % os.path.abspath(os.path.dirname(__file__)),
    }),

    (r'^', include('l2v.urls')),
)
