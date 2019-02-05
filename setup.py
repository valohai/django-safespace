import re

import setuptools

with open('./safespace/__init__.py', 'r') as infp:
    version = re.search("__version__ = ['\"]([^'\"]+)['\"]", infp.read()).group(1)

dev_dependencies = [
    'flake8',
    'isort',
    'pydocstyle',
    'pytest-cov',
    'pytest-django>=3.0.0',
]

if __name__ == '__main__':
    setuptools.setup(
        name='django-safespace',
        description='Exception catching and handling middleware for Django',
        version=version,
        url='https://github.com/valohai/django-safespace',
        author='Valohai',
        maintainer='Aarni Koskela',
        maintainer_email='akx@iki.fi',
        license='MIT',
        install_requires=['Django'],
        tests_require=dev_dependencies,
        extras_require={'dev': dev_dependencies},
        packages=setuptools.find_packages('.', exclude=('safespace_tests',)),
        include_package_data=True,
    )
