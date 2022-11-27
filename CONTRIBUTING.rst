Contributing to py-moneyed
==========================

If you would like to contribute to py-moneyed, the recommended workflow is:

1. First raise an issue on GitHub for any proposal or idea that might be
   controversial and get feedback from the maintainers. If you have something
   that is an obvious bug (a typo in the docs, for example), you can skip this
   step.

2. Fork the project and checkout your fork onto your development machine.

3. Create a virtualenv of some kind for development (venv_, virtualenv_ or
   virtualenvwrapper_) and install py-moneyed into it::

     python setup.py develop

4. Optional, but highly recommended to save time later - install `pre-commit
   <https://pre-commit.com/>`_ hooks::

     pip install pre-commit
     pre-commit install

5. Create a git branch for your changes, starting from ``master``

6. Fix the bug or implement your changes, being sure to:

   1. Add tests and docs
   2. Run the test suite (below)

7. Push your changes to your GitHub repo and submit a pull request.

Testing
-------

To run the test suite, first install tox (into your virtualenv)::

  pip install tox

Run the tests using tox::

  tox -e py310

You can run the test suite on all supported environments using tox_
(recommended). If you do not have all versions of Python that are used in
testing, you can use pyenv_ to install them, and you may benefit from the
additional plugin pyenv-implict_.

The py-moneyed package is tested against Python 3.7 - 3.11 and PyPy 3.

.. _tox: https://tox.readthedocs.io/en/latest/
.. _pyenv: https://github.com/pyenv/pyenv
.. _pyenv-implict: https://github.com/concordusapps/pyenv-implict
.. _venv: https://docs.python.org/3/library/venv.html
.. _virtualenv: https://virtualenv.pypa.io/en/stable/
.. _virtualenvwrapper: https://virtualenvwrapper.readthedocs.io/en/latest/
