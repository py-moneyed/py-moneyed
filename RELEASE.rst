Release process
===============

* Check that all tests are passing on GitHub Actions: https://github.com/py-moneyed/py-moneyed/actions?query=workflow%3Abuild+branch%3Amaster

* Change version number in:

  * setup.py
  * docs/conf.py

* Fix 'CHANGES.rst' so the top section says "[new version number] [date]"

* Commit to VCS

* Release to PyPI::

    $ ./release.sh

* Tag the release e.g.::

    git tag v0.7
    git push upstream --tags

Post release
~~~~~~~~~~~~

* Add new section to CHANGES.rst - "[next version number] (unreleased)"

* Add next version number plus "-dev" suffix in ``setup.py``, ``docs/conf.py``
