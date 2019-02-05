SECRET_KEY = 'safespace'
ROOT_URLCONF = 'safespace_tests.urls'

INSTALLED_APPS = (
    'safespace',
    'safespace_tests',
)

MIDDLEWARE = MIDDLEWARE_CLASSES = (
    'safespace.middleware.SafespaceMiddleware',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {},
    },
]

SAFESPACE_TEMPLATE_NAMES = [
    'error_{code}.html',
    'safespace/problem.html'
]


SAFESPACE_EXCEPTION_CLASSES = [
    'django.core.exceptions.ValidationError',
    'django.http.response.Http404',
    'safespace.excs.Problem',
    'safespace_tests.excs.CustomError',
]
