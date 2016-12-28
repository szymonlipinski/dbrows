#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

version = '0.5.0'

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
