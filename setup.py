#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ast
import os
from setuptools import setup, find_packages


def local_file(*f):
    with open(os.path.join(os.path.dirname(__file__), *f), "r") as fd:
        return fd.read()


class VersionFinder(ast.NodeVisitor):
    VARIABLE_NAME = "version"

    def __init__(self):
        self.version = None

    def visit_Assign(self, node):
        try:
            if node.targets[0].id == self.VARIABLE_NAME:
                self.version = node.value.s
        except Exception:
            pass


def read_version():
    finder = VersionFinder()
    finder.visit(ast.parse(local_file("application", "version.py")))
    return finder.version


setup(
    name="flask-hello",
    version=read_version(),
    description="\n".join(
        [
            "Application Belt is a command-line tool and python library",
            "to enhance the workflow of Application engineers.",
        ]
    ),
    long_description=local_file("README.rst"),
    entry_points={"console_scripts": ["flask-hello = application.cli:main"]},
    url="https://github.com/application/flask-hello",
    packages=find_packages(exclude=["*tests*"]),
    include_package_data=True,
    package_data={
        "application": [
            "README.rst",
            "*.png",
            "*.rst",
            "docs/*",
            "docs/*/*",
        ]
    },
    package_dir={"flask-hello": "application"},
    zip_safe=False,
    author="Application Inc.",
    author_email="dev@application.com",
    install_requires=local_file("requirements.txt").splitlines(),
    dependency_links=[],
)
