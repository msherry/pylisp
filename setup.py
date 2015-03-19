import re
from setuptools import setup, find_packages

packages = find_packages(
    '.',
    exclude=(
        'tests', 'tests.*',
        'db', 'db.*',
        'tools', 'tools.*',
    )
)

version = (
    re
    .compile(r".*__version__ = '(.*?)'", re.S)
    .match(open('pylisp/__init__.py').read())
    .group(1)
)

tests_require = [
    # 'mock >= 0.8, < 0.9',
    # 'nose',
    'pytest',
]

setup(
    name='pylisp',
    description='PyLisp',
    version=version,
    license='Apache',
    url='http://github.com/msherry/pylisp',
    author='Marc Sherry',
    author_email='msherry@gmail.com',
    packages=packages,
    scripts=[
        # 'bin/script1',
    ],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # 'balanced == 1.2',
        'ipdb',
    ],
    extras_require={
        'tests': tests_require,
    },
    tests_require=tests_require,
    test_suite='py.test',
)
