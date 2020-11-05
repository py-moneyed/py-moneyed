Release process
===============

* Check that all tests are passing on GitHub Actions: https://github.com/limist/py-moneyed/actions?query=workflow%3Abuild+branch%3Amaster

* Remove "-dev" suffix in setup.py, change version number if required.

* Fix 'CHANGES.rst' so the top section says "Changes in [new version number]"

* Commit to VCS

* Last checks::

    git status
    check-manifest
    flake8

* Release to PyPI::

    $ ./setup.py sdist bdist_wheel
    $ twine upload dist/*

* Tag the release e.g.::

    git tag v0.7

    git push upstream --tags

Post release
~~~~~~~~~~~~

* Add new section to CHANGES.rst - "Changes in development version"

* Add next version number plus "-dev" suffix in setup.py
