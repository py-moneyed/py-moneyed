from setuptools import setup, find_packages

setup(
    name='py-moneyed',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    version='0.5',
    description='Provides Currency and Money classes for use in your Python code.',
    author='Kai',
    author_email='k@limist.com',
    url='http://github.com/bearbones/py-moneyed',
    download_url='',
    keywords="money currency class abstraction",
    license='BSD',
    install_requires=[],
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Topic :: Office/Business :: Financial',
        'Topic :: Software Development :: Libraries :: Python Modules'],
    long_description=open('README.rst', 'r').read()
    )
