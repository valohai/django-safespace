from __future__ import unicode_literals

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin
from django.utils.encoding import force_str
from django.utils.text import camel_case_to_spaces
from django.utils.translation import gettext_lazy as _
from safespace.settings import get_exception_classes


class SafespaceMiddleware(MiddlewareMixin):
    """The main safespace middleware."""

    def process_exception(self, request, exception):
        """
        Possibly process an exception. This is a Django middleware hook.

        :param request: Django request that caused the exception
        :type request: django.http.HttpRequest
        :param exception: The exception that occurred
        :type exception: Exception
        :return: Response, maybe
        :rtype: django.http.HttpResponse|None
        """

        if self.should_handle_exception(request, exception):
            return self.respond_to_exception(request, exception)

    def should_handle_exception(self, request, exception):
        """
        Return true if Safespace should handle the exception.
        :param request: Django request that caused the exception
        :type request: django.http.HttpRequest
        :param exception: The exception that occurred
        :type exception: Exception
        :return:
        """
        return any(isinstance(exception, klass) for klass in get_exception_classes())

    def respond_to_exception(self, request, exception):
        """
        Get a response for the given request and exception.

        :param request: Django request that caused the exception
        :type request: django.http.HttpRequest
        :param exception: The exception that occurred
        :type exception: Exception
        :return: Response
        :rtype: django.http.HttpResponse
        """

        # If the exception has a `response`, return that.
        response = getattr(exception, 'response', None)
        if response and isinstance(response, HttpResponse):
            return response

        context = self.get_context(request, exception)

        response_type = self.determine_response_type(request, exception)
        response_renderer = getattr(self, 'get_%s_response' % response_type)
        status = self.get_response_status(request, exception)
        response = response_renderer(request, exception, context, status)
        if context['code']:
            response['X-Error-Code'] = context['code']
        return response

    def get_html_response(self, request, exception, context, status):
        return render(
            request=request,
            template_name=self.get_template_names(request, exception, context),
            context=context,
            using=getattr(settings, 'SAFESPACE_TEMPLATE_ENGINE', None),
            status=status,
        )

    def get_json_response(self, request, exception, context, status):
        content = {
            'code': context['code'],
            'error': context['message'],
            'title': context['title'],
        }
        return JsonResponse(content, status=status)

    def get_response_status(self, request, exception):
        """
        Get the HTTP status code for the response.

        This could be overridden in a subclass.

        :param request: Django request that caused the exception
        :type request: django.http.HttpRequest
        :param exception: The exception that occurred
        :type exception: Exception
        """

        return getattr(settings, 'SAFESPACE_HTTP_STATUS', 406)

    def get_template_names(self, request, exception, context):
        """
        Get candidate template names for rendering a response.

        This could be overridden in a subclass.

        :param request: Django request that caused the exception
        :type request: django.http.HttpRequest
        :param exception: The exception that occurred
        :type exception: Exception
        :param context: Precalculated dict of template interpolation variables
        :type context: dict

        :return: List of template names
        :rtype: list[str]
        """
        return [
            template_name.format(**context)
            for template_name in getattr(
                settings, 'SAFESPACE_TEMPLATE_NAMES', ['safespace/problem.html']
            )
        ]

    def get_context(self, request, exception):
        """
        Get a context dictionary with various context data.

        This is used both for template name determination
        as well as template rendering.

        :param request: Django request that caused the exception
        :type request: django.http.HttpRequest
        :param exception: The exception that occurred
        :type exception: Exception
        :returns: Variables
        :rtype: dict[str, object]
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

    def determine_response_type(self, request, exception):
        """
        Determine what type of response to emit.

        Currently supported: "json" -- anything else will
        result in the standard HTML template response.

        :param request: Django request that caused the exception
        :type request: django.http.HttpRequest
        :param exception: The exception that occurred
        :type exception: Exception
        :return: type string
        :rtype: str
        """
        # Simulate `request.is_ajax()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return 'json'
        if 'application/json' in request.META.get('HTTP_ACCEPT', ''):
            # Nb: this does not take different q= values into account,
            #     but that's probably okay.
            return 'json'

        return 'html'
