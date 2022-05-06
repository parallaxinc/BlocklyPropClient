BlocklyPropClient
=======================

# Introduction
The BlocklyPropClient is a vital part of the https://solo.parallax.com system that must be installed and run locally on the user's computer to complete the connection to the target Propeller microcontroller product. It provides local connection features- downloading your programs into the Propeller-based product.

This version of the BlocklyProp Client is written to be compatible with BlocklyProp Solo. BlocklyProp Client is a Python client for BlocklyProp Solo https://solo.parallax.com.
It received compiled code from BlocklyProp Solo through a websocket and uses the proploader executable to program the propeller.

Motivation
---------------
Although Python 2.7 is now deprecated and BlocklyProp launcher work really well across a number of operating systems including chromebooks. Since, the release of BlocklyProp Launcher it is no longer possible to program older Scribbler S2 robots through BlocklyProp. 

GUI is also now old and no longer works on latest versions of windows.
Using this client allows leveraging the modern BlocklyProp programming interface while extending the older Scribbler S2 hardware a little further.


Running
-----------------

BlocklyPropClient has been written using Python 2.7

You will first have to install some python dependencies before you can run BlocklyPropClient.

* ws4py
* pyserial
* cherrypy

These can all be installed using the auto-installer by running the following in the terminal: 'python InstallDependencies.py'

Then do: 

`python BlocklyPropClient.py`

Building
-----------------

If you want to create an executable to distribute to users:

_Python 2.7 is deprecated, last version of PyInstaller to support Python 2.7 is version 3.6_

Install pyinstaller:

`python -m pip install PyInstaller==3.6`

Run pyinstaller:

`pyinstaller BlocklyPropClient.xxxxxxx.spec`

where you replace xxxxx by your OS. The distributable folder is available under the dist directory.

If you run the executable inside this directory, python nor any of the dependencies need to be installed on that computer.


# Wiki
Visit the [BlocklyPropClient Wiki](https://github.com/parallaxinc/BlocklyPropClient/wiki) for more information.
