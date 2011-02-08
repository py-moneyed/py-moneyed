from setuptools import setup, find_packages

setup(
    name='python-money',
    version='0.2',
    url='http://github.com/limist/python-money',
    license='BSD',
    author='Kai',
    author_email='k@limist.com',
    description='python-money provides re-usable Currency and Money classes for working with money and currencies in your own software.',
    keywords="money currency class abstraction",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=['setuptools'],
    )
