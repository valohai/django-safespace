# django-safespace

[![Build Status](https://travis-ci.org/valohai/django-safespace.svg?branch=master)](https://travis-ci.org/valohai/django-safespace)
[![codecov](https://codecov.io/gh/valohai/django-safespace/branch/master/graph/badge.svg)](https://codecov.io/gh/valohai/django-safespace)


An exception handling middleware.

## Installation

* Add `safespace` to your `INSTALLED_APPS`.
* Add `safespace.middleware.SafespaceMiddleware` to your `MIDDLEWARE_CLASSES`.
* See below for customization.

## Usage

* Raise a `safespace.excs.Problem` anywhere in your code and have it rendered
  as a template (or, if the request was AJAX, as JSON).
* Raise any exception (that is processed by Safespace at all)
  with a `response` attribute holding a Django `HTTPResponse`
  to have that `response` returned.  Useful for those exceptional cases
  where you just need to respond something from 50 levels deep in a call stack.

## Settings

* `SAFESPACE_TEMPLATE_NAMES`:
   A list of paths to Django templates. These are actually
   [Python `.format` template strings][ts], which will be interpolated
   with variables described below. As usual with lists of templates in
   Django, the first template to exist will be used for the rendering.
* `SAFESPACE_TEMPLATE_ENGINE`:
   Which named template engine to use to render error templates.
   Defaults to `None`, i.e. let Django decide.
* `SAFESPACE_EXCEPTION_CLASSES`:
   A list of classnames (dotted paths) to be caught by the middleware.
   Naturally subclasses of the given exceptions will also be caught.
   This defaults to processing `safespace.excs.Problem`s and
   `django.core.exceptions.ValidationError`s.
* `SAFESPACE_HTTP_STATUS` (integer):
   The HTTP status code for the exception responses. Defaults to
   "406 Not Acceptable", which may or may not be what you want, but it
   sure as heck is better than "200 OK" for errors.
   
[ts]: https://docs.python.org/2/library/string.html#format-string-syntax

## Template variables

The following variables are available for interpolation in the
`SAFESPACE_TEMPLATE_NAMES` settings variable and as context in the template rendered:

* `{exc_type}`: The exception's class name, with CamelCase converted
                to snake_case. E.g. `ValueError` is `value_error`.
* `{namespace}`: The namespace from the request's [resolver match][rm].
* `{app_name}`: The application name from the request's [resolver match][rm].
* `{url_name}`: The URL name from the request's [resolver match][rm].
* `{view_name}`: The view name from the request's [resolver match][rm].
* `{code}`: Exception `code` attribute, if any.
* `{title}`: Exception `title` attribute, if any.
* `{exception}`: The exception itself. This makes no sense in interpolation.
* `{message}`: The exception message.
                 
[rm]: https://docs.djangoproject.com/en/1.10/ref/urlresolvers/#django.urls.ResolverMatch
                 
## Development & tests

In general, running `tox` will test everything on every supported
platform.  For development, though,

* Install development deps: `pip install -e .[dev]`
* Run tests: `py.test`
