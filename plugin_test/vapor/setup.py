from os.path import join, dirname
from setuptools import setup, find_packages

setup(
    name="Vapor",
    version="0.1",
    description="Open Stack contrail plugin test suite.",
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.rst')).read(),
    install_requires=['pytest'],
)
