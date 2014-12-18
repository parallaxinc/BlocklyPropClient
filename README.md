BlocklyPropClient
=======================

Introduction
-----------------

The BlocklyPropClient is a Python client for the hosted version of BlocklyProp.
It provides the spin and Prop-C compiler, it can load your programs in to the prop and creates a serial connection from the browser to the propeller.

Running
-----------------

BlocklyPropClient has been written using Python 2.7

You will first have to install some python dependencies before you can run BlocklyPropClient.

* ws4py
* pyserial
* cherrypy

These can all be installed using the auto-installer by running the following in the terminal: 'python InstallDependencies.py'

Then do: python BlocklyPropClient.py

Building
-----------------

If you want to create an executable to distribute to users:

Install pyinstaller (using pip) and do:
pyinstaller BlocklyPropClient.xxxxxxx.spec

where you replace xxxxx by your OS. The distributable folder is available under the dist directory.

If you run the executable inside this directory, python nor any of the dependencies need to be installed on that computer.
