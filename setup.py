

from setuptools import setup, find_packages

setup(
    name='qkit',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'scipy',
        'matplotlib',
        'h5py',
        'pyvisa-py',
        'pyqt5',

    ],
)

# INSTALL USING THE FOLLOWING COMMAND
# python setup.py install -e .

# . indicates that we’re installing the package in the current directory. -e indicates that the package should be editable. That means that if you change the files inside the src folder, you don’t need to re-install the package for your changes to be picked up by Python.
