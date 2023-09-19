.. include:: global.rst.inc
.. _installation:

Installation
============

Qkit requires:

* Python_ >= 3.5
* some python dependencies, see requirements.txt

Currently, only installation from git repo checkout is supported.

You need Anaconda, so go to: https://www.anaconda.com/ and install it. Remember to tick the
box regarding the installation of Conda in your PATH variable.
Open the command prompt with the Conda environment in it and install Git by typing::
        conda install git
It's better to create a new environment and activate it.
Create a folder where you want to clone the Qkit repository.
Go to the command prompt and type::

        git clone https://github.com/QuantumCircuitsGlasgow/qkit-gla.git

Navigate to the folder using ::

        cd qkit-gla

and install all the packages with ::

        pip install -r requirements.txt

Go to 'Advanced system settings' -> 'Environment variables' and check if there is a 'PYTHONPATH' entry under user variables.
If it doesn't exist, create it.
Double-click on it and copy the path of the Qkit folder. Click 'OK' and exit.
To test if everything went well, open Jupyter Notebook and execute::
        import qkit
        qkit.start()
This function executes a set of init routines located in qkit/core/s_init/

