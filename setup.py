#!/usr/bin/env python

import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand


class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import tox

        errno = tox.cmdline(self.test_args)
        sys.exit(errno)


setup(
    name="py-moneyed",
    packages=find_packages(where="src"),
    version="1.2",
    description="Provides Currency and Money classes for use in your Python code.",
    author="Kai",
    author_email="k@limist.com",
    maintainer="Dmitry Dygalo",
    maintainer_email="dadygalo@gmail.com",
    url="http://github.com/py-moneyed/py-moneyed",
    download_url="",
    keywords="money currency class abstraction",
    license="BSD",
    install_requires=[
        "babel>=2.8.0",
        "typing-extensions>=3.7.4.3",
    ],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Development Status :: 6 - Mature",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    long_description=open("README.rst").read(),
    long_description_content_type="text/x-rst",
    extras_require={"tests": ["pytest>=2.3.0", "tox>=1.6.0"]},
    tests_require=["tox>=1.6.0", "pytest>=2.3.0"],
    cmdclass={"test": Tox},
    include_package_data=True,
    package_dir={"": "src"},
)
