from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys

class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import tox
        errno = tox.cmdline(self.test_args)
        sys.exit(errno)

setup(
    name='py-moneyed',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    version='0.5.0',
    description='Provides Currency and Money classes for use in your Python code.',
    author='Kai',
    author_email='k@limist.com',
    url='http://github.com/limist/py-moneyed',
    download_url='',
    keywords="money currency class abstraction",
    license='BSD',
    install_requires=[],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Topic :: Office/Business :: Financial',
        'Topic :: Software Development :: Libraries :: Python Modules'],
    long_description=open('README.rst', 'r').read(),
    extras_require={
        'tests': [
            'pytest>=2.3.0',
            'tox>=1.6.0'
        ]},
    tests_require=['tox>=1.6.0', 'pytest>=2.3.0'],
    cmdclass={'test': Tox},
    include_package_data=True,
    )
