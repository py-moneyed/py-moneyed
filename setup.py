from setuptools import setup, find_packages

setup(
    name='moneyed',
    version='0.2',
    url='http://github.com/limist/moneyed',
    license='BSD',
    author='Kai',
    author_email='k@limist.com',
    description='The moneyed Python package provides re-usable Currency and Money classes for working with money and currencies in your Python code.',
    keywords="money currency class abstraction",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=['setuptools'],
    )
