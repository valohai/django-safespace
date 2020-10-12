from django.urls import re_path
from safespace_tests.views import (
    custom_error_view,
    database_error_view,
    exception_response_view,
    four_oh_four_view,
    problem_view,
)

urlpatterns = [
    re_path('^problem/$', problem_view),
    re_path('^custom/$', custom_error_view),
    re_path('^db/$', database_error_view),
    re_path('^404/$', four_oh_four_view),
    re_path('^exception-response/$', exception_response_view),
]
