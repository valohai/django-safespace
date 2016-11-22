import setuptools

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
        version='0.1.0',
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
