#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

version = '0.6.0'


class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        pytest.main(self.test_args)


setup(
    name='dbrows',
    version=version,
    description="A nice interface for SQL databases.",
    long_description="",
    author="Szymon Lipiński",
    author_email='mabewlun@gmail.com',
    url='https://github.com/szymonlipinski/dbrows',
    packages=find_packages(),
    license='MIT',
    install_requires=['six'],
    test_suite='tests',
    tests_require=['pytest', 'tox', 'psycopg2'],
    cmdclass={'test': PyTest},
    classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Natural Language :: English',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Topic :: Database',
    ],
)
