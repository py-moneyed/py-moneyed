#!/bin/sh

# See RELEASE.rst notes

set -x

# Basic tests
check-manifest || exit 1
isort || exit 1
flake8 || exit 1
py.test || exit 1

umask 000
rm -rf build dist
git ls-tree --full-tree --name-only -r HEAD | xargs chmod ugo+r
find . -type d | xargs chmod ugo+rx

./setup.py sdist bdist_wheel || exit 1

VERSION=$(./setup.py --version) || exit 1

# twine upload dist/py-moneyed-$VERSION.tar.gz dist/py_moneyed-$VERSION-py2.py3-none-any.whl || exit 1
