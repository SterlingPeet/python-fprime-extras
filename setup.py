#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import io
import re
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext
import subprocess

from setuptools import find_packages
from setuptools import setup

__version__ = '0.0.0'


def read(*names, **kwargs):
    with io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ) as fh:
        return fh.read()

def get_version():
    version = __version__
    branch = None
    try:
        version = subprocess.check_output(["git", "describe", "--tags", "--always"]).decode("utf-8").strip()
        try:
            branch = subprocess.check_output(["git", "branch", "--show-current"]).decode("utf-8").strip()
        except:
            branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode("utf-8").strip()
        version = version + '-' + branch.replace(' ', '_').replace('/', '_').replace('\\', '_').replace('-', '_')
        with open('src/fprime_extras/version.py', 'w') as f:
            f.write('__version__ = \'{}\'\r\n__branch__ = \'{}\'\r\n'.format(version, branch))
    except:
        version = __version__
    return version


setup(
    name='fprime-extras',
    version=get_version(),
    license='MIT',
    description='Extra tools for working with F Prime projects.',
    long_description='%s\n%s' % (
        re.compile('^.. start-badges.*^.. end-badges', re.M | re.S).sub('', read('README.rst')),
        re.sub(':[a-z]+:`~?(.*?)`', r'``\1``', read('CHANGELOG.rst'))
    ),
    author='Sterling Lewis Peet',
    author_email='sterling.peet@gatech.edu',
    url='https://github.com/SterlingPeet/python-fprime-extras',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Utilities',
    ],
    project_urls={
        'Documentation': 'https://python-fprime-extras.readthedocs.io/',
        'Changelog': 'https://python-fprime-extras.readthedocs.io/en/latest/changelog.html',
        'Issue Tracker': 'https://github.com/SterlingPeet/python-fprime-extras/issues',
    },
    keywords=[
        # eg: 'keyword1', 'keyword2', 'keyword3',
    ],
    python_requires='>=3.5',
    install_requires=[
        'appdirs',
        'requests',
        'lxml',
    ],
    extras_require={
        # eg:
        #   'rst': ['docutils>=0.11'],
        #   ':python_version=="2.6"': ['argparse'],
    },
    entry_points={
        'console_scripts': [
            'fprime-extras = fprime_extras.cli:main',
        ]
    },
)
