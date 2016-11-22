from django.conf.urls import url

from safespace_tests.views import custom_error_view, database_error_view, exception_response_view, problem_view

urlpatterns = [
    url('^problem/$', problem_view),
    url('^custom/$', custom_error_view),
    url('^db/$', database_error_view),
    url('^exception-response/$', exception_response_view),
]
