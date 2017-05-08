Release process
===============

* Check that all tests are passing on Travis: https://travis-ci.org/limist/py-moneyed

* Increment version number in setup.py

* Fix 'CHANGES.rst' so the top section says "Changes in [new version number]"

* Commit to VCS

* Last checks::

    git status
    check-manifest
    flake8

* Release to PyPI::

    ./setup.py sdist bdist_wheel register upload

* Add new section to CHANGES.rst - "Changes in development version"
