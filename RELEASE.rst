Release process
===============

* Check that all tests are passing on Travis: https://travis-ci.org/limist/py-moneyed

* Remove "-dev" suffix in setup.py, change version number if required.

* Fix 'CHANGES.rst' so the top section says "Changes in [new version number]"

* Commit to VCS

* Last checks::

    git status
    check-manifest
    flake8

* Release to PyPI::

    ./setup.py sdist bdist_wheel register upload

* Tag the release e.g.::

    git tag v0.7

    git push --tags

Post release
~~~~~~~~~~~~

* Add new section to CHANGES.rst - "Changes in development version"

* Add next version number plus "-dev" suffix in setup.py
