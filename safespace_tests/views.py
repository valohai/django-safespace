from django.db import DatabaseError
from django.http import HttpResponse

from safespace.excs import Problem
from safespace_tests.excs import CustomError


def problem_view(request):
    raise Problem(
        'A woeful error',
        title='Oh no!',
        code=request.GET.get('code'),
    )


def custom_error_view(request):
    raise CustomError('Oopsy daisy!')


def database_error_view(request):
    raise DatabaseError('MongoDB: Unable to find libwebscale.so')


def exception_response_view(request):
    exc = Problem('foo')
    exc.response = HttpResponse('nice.')
    raise exc  # You can imagine this is 20 callstack levels deep.
