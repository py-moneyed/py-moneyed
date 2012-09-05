from setuptools import find_packages
from setuptools import setup

setup(
    name='py-moneyed',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    version='0.4',
    description='Provides Currency and Money classes for use in your Python code.',
    author='Kai',
    author_email='k@limist.com',
    url='http://github.com/limist/py-moneyed',
    download_url='',
    keywords="money currency class abstraction",
    license='BSD',
    install_requires=[
        'setuptools'],
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Topic :: Office/Business :: Financial',
        'Topic :: Software Development :: Libraries :: Python Modules'],
    long_description=open('README', 'r').read())
