from setuptools import setup, find_packages

setup(
    name = 'python-money',
    version = '0.2',
    url = 'http://github.com/limist/python-money',
    license = 'BSD',
    description = 'python-money provides carefully designed basic Python primitives for working with money and currencies.',
    author = 's3x3y1, ppr.vitaly, efilipov@mlke.net, Kai Wu',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    install_requires = ['setuptools'],
    )
