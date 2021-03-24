#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

version = "1.1.0"

install_requires = []

tests_require = ["pytest==6.2.2", "pytest-runner"]
dev_require = ["black==19.3b0"]


extras_require = {
    "postgres": ["psycopg2==2.8.6"],
    "mysql": [],
    "dev": dev_require,
    "testing": tests_require,
}

setup(
    # python_requires=">=3",
    name="dbrows",
    version=version,
    description="A better interface for SQL databases.",
    long_description="",
    author="Szymon Lipiński",
    author_email="mabewlun@gmail.com",
    url="https://github.com/szymonlipinski/dbrows",
    packages=find_packages(),
    license="MIT",
    install_requires=install_requires,
    extras_require=extras_require,
    setup_requires=["pytest-runner"],
    test_suite='pytest',
    tests_require=tests_require,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python::3",
        "Programming Language :: Python::3::Only",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Database",
        "Topic :: Database :: Front-Ends",
        "Topic :: Software Development :: Libraries",
    ],
)
