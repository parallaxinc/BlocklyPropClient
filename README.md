BlocklyPropClient
=======================

# Introduction
--------------

The BlocklyPropClient is a client for the http://blockly.parallax.com system.
It provides local Propeller connection features- downloading your programs into the Propeller and creating a serial connection between the Propeller and the browser.

BlocklyPropClient is written using Python v2.7.

  
# Running
---------

Installations are self-contained; no extra dependencies are required except for USB drivers for Parallax development boards.

## Running on Linux
You will first have to install some python dependencies before you can run BlocklyPropClient.

* ws4py
* pyserial
* cherrypy

These can all be installed using the auto-installer by running the following in the terminal: 'python InstallDependencies.py'

Then execute: python BlocklyPropClient.py


# Developers
------------

To build and package BlocklyProp Client, configure your system and then perform the appropriate build and package steps below.

## System Configuration
These configurations steps need only be done once per system.

### Windows Configuration

  * __IMPORTANT:__ Don't use _McAfee_ (or possibly any anti-virus) on build system - it prevents proper builds of BlocklyPropClient installer
  * Install _Git_
  * Install _Python v2.7.12_ 64-bit / 32-bit (as appropriate)
    * [https://www.python.org/downloads/release/python-2712/](https://www.python.org/downloads/release/python-2712/)
    * Use standard destination
  * Install _PyCharm v2016.2.3_ - Community Edition - this is convienent for package installation
    * [https://confluence.jetbrains.com/display/PYH/Previous+PyCharm+Releases](https://confluence.jetbrains.com/display/PYH/Previous+PyCharm+Releases)
    * Check option to create desktop shortcut
    * Uncheck .py association
  * Run PyCharm (be patient, it takes a long time to start sometimes) and then...
    * If prompted, select _I do not have a previous version..._
    * Allow default options on _Initial Configuration_ dialog
    * Select _Check out from Version Control > Git_
    * Set _Git Repository URL:_ to __https://github.com/parallaxinc/BlocklyPropClient.git__
    * Click _Test_ button
    * If test successfull, click the _Clone_ button
    * Choose to open the project's directory
    * Select _File > Settings..._
    * Expand the _BlocklyPropClient_ item
    * Select _Project Interpreter_
    * In the right pane, select the _+_ button (_Install_)
      * If the _+_ button is grayed out, try closing the _Settings_ window and reopening it again
    * In the _Available Packages_ window
      * Uncheck the _Install to user's site packages directory..._ item
      * Search for and _Install Package_ for each of the items below
        * Install _ws4py v0.3.5+_
        * Install _CherryPy v8.1.0_    (Select _CherryPy_, check the _Specify version_ box, and select _8.1.0_)
        * Install _pyserial v3.1.1_    (Select _pyserial_, check the _Specify version_ box, and select _v3.1.1_)
        * Install _PyInstaller v3.1.1_ (Select _PyInstaller_, check the _Specify version_ box and select _v3.1.1_)
          * Do not use v3.2 as it creates an msc..100 dependency
     * Close the _Available Packages_ window
     * Click the _Apply_ button (if available) on the _Settings_ window
     * Click _OK_ on the _Settings_ window
     * Wait for the installation steps (status bar of PyCharm) to finish
     * Exit PyCharm
  * Install _Innosetup 5.5.9 (non-Unicode)_
    * [http://www.jrsoftware.org/isdl.php](http://www.jrsoftware.org/isdl.php)
    * Check _Install Inno Setup Preprocessor_ option
    * Check _Create a desktop shortcut_ option
    * If you chose to run Inno Setup, just close the _Open_ dialog for now

### Mac Configuration
* Open Terminal (Mac command-line)
  * Install _Git_ if necessary
  * Install _Homebrew_
    * _$ /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"_
  * Install _Python_ (_v2.7.13_ at the time of this writing; v2.7.12 and v2.7.13 are known to work for BlocklyPropClient)
    * _$ brew install python_
  * Install _VirtualEnv_ package
    * _$ pip install virtualenv_
  * Create _PythonProjects_ folder
    * _$ cd ~/_
    * _$ mkdir PythonProjects_
    * _$ cd PythonProjects_
  * Check out the needed branch from the _BlocklyPropClient_ repository
    * _$ git clone https://github.com/parallaxinc/BlocklyPropClient.git_
    * _$ cd BlocklyPropClient_
    * _$ git checkout {branch}_
  * Create a _Virtual Python_ environment inside the repository's work folder
    * _$ virtualenv VPython --distribute_
  * Activate the _Virtual Python_ environment for BlocklyPropClient
    * _$ source VPython/bin/activate_
  * Install all required packages for BlocklyPropClient
    * Install _ws4py v0.3.5+_
      * _(VPython)$ pip install ws4py==0.3.5_
    * Install _CherryPy v8.1.0_
      * _(VPython)$ pip install CherryPy==8.1.0_
    * _Install pyserial v3.1.1_
      * _(VPython)$ pip install pyserial==3.1.1_
    * Install _PyInstaller v3.1.1_ (Do not use v3.2 as it creates an msc..100 dependency)
      * _(VPython)$ pip install PyInstaller==3.1.1_
  * Deactivate the _Virtual Environment..._
    * _(VPython)$ deactivate_
      * The "(VPython)" prefix will now disappear from your command-line

## Building & Packaging
These steps need be performed frequently, as needed, after System Configuration (above).

### Windows Building & Packaging

  * Build the BlocklyPropClient
    * Open a command window
    * Check out the needed branch from the _BlocklyPropClient_ repository
      * This can be done either 
        * in _PyCharm's VCS > Git > Branches..._ menu, then select _origin/{branch} > Checkout as new local branch_ from _Remote Branches_ (or if _Local Branches_ section exists, you can select _{branch} -> origin/{branch}_ from _Local Branches_), then Exit PyCharm
        * in Git command line: 
          * _$ cd C:\Users\{username}\PycharmProjects\BlocklyPropClient_
          * _$ git checkout origin {branch}_
    * Run the build script (.windows.spec) from within the repository directory:
      * _$ c:\Python27\Scripts\pyinstaller BlocklyPropClient.windows.spec_
        * This builds and stores the application files in the __./dist__ subfolder which will be used by InnoSetup.
  * Package BlocklyPropClient
    * Run InnoSetup
      * _File > Open_ the .spec file: _C:\Users\{username}\PycharmProjects\BlocklyPropClient\package\blocklypropclient-installer.iss_
      * Select _Build > Compile_
    * Now the installer executable will be in the __./dist__ subfolder.

### Mac Building & Packaging

  * Open a terminal (command-line)
  * Navigate to the project
    * _$ cd ~/PythonProjects/BlocklyPropClient_
  * Check out the needed branch from the _BlocklyPropClient_ repository
    * _$ git checkout {branch}_
  * Activate the _Virtual Python_ environment for BlocklyPropClient
    * _$ source VPython/bin/activate_
  * Build BlocklyPropClient
    * (VPython)$ PyInstaller BlocklyPropClient.macos.spec
      * This builds and stores the application bundle in the ./dist subfolder as BlocklyPropClient.app
  * Sign and Package BlocklyPropClient (requires signing certificate in Mac's KeyChain)
    * Navigate to the package folder
      * cd package
    * Run the mac_sign_and_package script giving the proper version number and deploy option
      * To include the FTDI USB Drivers inside the installer:
        * ./mac_app_sign_and_package.sh -a "BlocklyPropClient" -v 0.5.1 -r -f -d
      * To exclude the FTDI USB Drivers from the installer:
        * ./mac_app_sign_and_package.sh -a "BlocklyPropClient" -v 0.5.1 -d
    * The installer package will be written to the ../dist subfolder as BlocklyPropClient-0.5.1-setup-MacOS.pkg
  * Deactivate the Virtual Environment...
      * (VPython)$ deactivate
        * The "(VPython)" prefix will now disappear from your command-line

