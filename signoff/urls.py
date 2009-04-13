from django.conf.urls.defaults import *

urlpatterns = patterns('signoff.views',
    (r'^\/?$', 'index'),
    (r'^\/locales\/?$', 'locale_list'),
    (r'^\/locales\/(?P<loc>[^\/]+)', 'milestone_list'),
    (r'^\/milestones\/?$', 'milestone_list'),
    (r'^\/milestones\/(?P<ms>.+)$', 'locale_list'),
    (r'^\/(?P<arg>\S+)?\/(?P<arg2>\S+)?$', 'sublist'),
)
