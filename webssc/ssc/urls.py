from django.conf.urls import patterns, url
from django.views.generic import TemplateView

urlpatterns = patterns('',
    url(r'^$', 'ssc.views.http_request', name='http'),
    url(r'^ajax/$', 'ssc.views.ajax_request', name='ajax'),
    url(r'^xml/$', 'ssc.views.xml', name='xml'),

    url(r'^accounts/login/$', 'ssc.views.user_login', name='login'),
    url(r'^accounts/login/welcome/$', TemplateView.as_view(template_name='ssc/welcome.html'), name='welcome'),

    url(r'^accounts/logout/$', 'ssc.views.user_logout', name='logout'),
    url(r'^accounts/logout/goodbye/$', TemplateView.as_view(template_name='ssc/goodbye.html'), name='goodbye'),

)
