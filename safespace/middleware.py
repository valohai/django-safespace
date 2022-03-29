from typing import Any, Dict, List, Optional

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin
from django.utils.encoding import force_str
from django.utils.text import camel_case_to_spaces
from django.utils.translation import gettext_lazy as _

from safespace.excs import Problem
from safespace.settings import get_exception_classes

ContextDict = Dict[str, Any]


class SafespaceMiddleware(MiddlewareMixin):
    """The main safespace middleware."""

    def process_exception(
        self, request: HttpRequest, exception: Exception
    ) -> Optional[HttpResponse]:
        """
        Possibly process an exception. This is a Django middleware hook.

        :param request: Django request that caused the exception
        :param exception: The exception that occurred
        :return: Response, maybe
        """
        if self.should_handle_exception(request, exception):
            return self.respond_to_exception(request, exception)
        return None

    def should_handle_exception(
        self, request: HttpRequest, exception: Exception
    ) -> bool:
        """
        Return true if Safespace should handle the exception.

        :param request: Django request that caused the exception
        :param exception: The exception that occurred
        """
        return any(isinstance(exception, klass) for klass in get_exception_classes())

    def respond_to_exception(
        self, request: HttpRequest, exception: Exception
    ) -> HttpResponse:
        """
        Get a response for the given request and exception.

        :param request: Django request that caused the exception
        :param exception: The exception that occurred
        :return: Response
        """
        # If the exception has a `response`, return that.
        response = getattr(exception, 'response', None)
        if response and isinstance(response, HttpResponse):
            return response

        context = self.get_context(request, exception)

        response_type = self.determine_response_type(request, exception)
        response_renderer = getattr(self, f'get_{response_type}_response')
        status = self.get_response_status(request, exception)
        response = response_renderer(request, exception, context, status)
        if not isinstance(response, HttpResponse):
            raise ImproperlyConfigured(
                f'Response renderer did not return a response, it returned {response!r}'
            )
        if context['code']:
            response['X-Error-Code'] = context['code']
        return response

    def get_html_response(
        self,
        request: HttpRequest,
        exception: Problem,
        context: ContextDict,
        status: int,
    ) -> HttpResponse:
        """Get a HTML response for a given request, exception, and context."""
        return render(
            request=request,
            template_name=self.get_template_names(request, exception, context),
            context=context,
            using=getattr(settings, 'SAFESPACE_TEMPLATE_ENGINE', None),
            status=status,
        )

    def get_json_response(
        self,
        request: HttpRequest,
        exception: Problem,
        context: ContextDict,
        status: int,
    ) -> JsonResponse:
        """Get a JSON response for a given request, exception, and context."""
        content = {
            'code': context['code'],
            'error': context['message'],
            'title': context['title'],
        }
        return JsonResponse(content, status=status)

    def get_response_status(self, request: HttpRequest, exception: Exception) -> int:
        """
        Get the HTTP status code for the response.

        This could be overridden in a subclass.

        :param request: Django request that caused the exception
        :param exception: The exception that occurred
        """
        return getattr(settings, 'SAFESPACE_HTTP_STATUS', 406)

    def get_template_names(
        self, request: HttpRequest, exception: Exception, context: ContextDict
    ) -> List[str]:
        """
        Get candidate template names for rendering a response.

        This could be overridden in a subclass.

        :param request: Django request that caused the exception
        :param exception: The exception that occurred
        :param context: Precalculated dict of template interpolation variables

        :return: List of template names
        """
        return [
            template_name.format(**context)
            for template_name in getattr(
                settings, 'SAFESPACE_TEMPLATE_NAMES', ['safespace/problem.html']
            )
        ]

    def get_context(self, request: HttpRequest, exception: Exception) -> ContextDict:
        """
        Get a context dictionary with various context data.

        This is used both for template name determination
        as well as template rendering.

        :param request: Django request that caused the exception
        :param exception: The exception that occurred
        :returns: Variables
        """
        resolver_match = getattr(request, 'resolver_match', None)
        exc_type = camel_case_to_spaces(exception.__class__.__name__).replace(' ', '_')
        env = {
            'exception': exception,
            'message': force_str(exception),
            'code': getattr(exception, 'code', None),
            'title': (getattr(exception, 'title', None) or _('Error')),
            'exc_type': exc_type,
            'view_name': getattr(resolver_match, 'view_name', None),
            'url_name': getattr(resolver_match, 'url_name', None),
            'app_name': getattr(resolver_match, 'app_name', None),
            'namespace': getattr(resolver_match, 'namespace', None),
        }
        return env

    def determine_response_type(
        self, request: HttpRequest, exception: Exception
    ) -> str:
        """
        Determine what type of response to emit.

        Currently supported: "json" -- anything else will
        result in the standard HTML template response.

        :param request: Django request that caused the exception
        :param exception: The exception that occurred
        :return: type string
        """
        # Simulate `request.is_ajax()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return 'json'
        if 'application/json' in request.META.get('HTTP_ACCEPT', ''):
            # Nb: this does not take different q= values into account,
            #     but that's probably okay.
            return 'json'

        return 'html'
