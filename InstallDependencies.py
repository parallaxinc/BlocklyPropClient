#This file will automatically install all of the dependencies for the BlocklyPropClient

#Author: valetolpegin@gmail.com ( Vale Tolpegin )

#Copyright 2014 Vale Tolpegin.
#
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

#This method will install and test the dependencies
def install():
    #Installing each dependency that is not already installed ( we do not want duplicates or any errors to occur because of this )
    
    print ""
    print "Beginning installation....."
    print ""
    
    #------------------------------------------------------------------------------------
    #Installing CherryPy and testing to see if the installation was successful
    
    os.chdir( "dependencies/CherryPy/" )

    version = os.system( 'python -c "import cherrypy;print cherrypy.__version__"' )
    if ( version != 0 ):
        os.system( "python setup.py install" )

        print ""
        print "CherryPy installation complete"
        print ""

        version = os.system( 'python -c "import cherrypy;print cherrypy.__version__"' )
        if ( version != 0 ):
            print ""
            print "ERROR......INSTALLATION OF CherryPy HAS FAILED"
            print ""
            exit()
    else:
        print ""
        print "CherryPy already installed.....moving on to next installation"
        print ""
    
    #------------------------------------------------------------------------------------
    #Installing PySerial and testing to see if the installation was successful
    
    os.chdir( "../pyserial" )

    version = os.system( 'python -c "import serial;print serial.Serial()"' )
    if ( version != 0 ):
        os.system( "python setup.py install" )

        print ""
        print "PySerial installation complete"
        print ""

        version = os.system( 'python -c "import serial;print serial.Serial()"' )
        if ( version != 0 ):
            print ""
            print "ERROR......INSTALLATION OF PySerial HAS FAILED"
            print ""
            exit()
    else:
        print ""
        print "PySerial already installed.....moving on to next installation"
        print ""

    #------------------------------------------------------------------------------------
    #Installing ws4py and testing to see if the installation was successful
    
    os.chdir( "../ws4py" )

    version = os.system( 'python -c "import ws4py;print ws4py.__version__"' )
    if ( version != 0 ):
        os.system( "python setup.py install" )
    
        print ""
        print "ws4py installation complete"
        print ""

        version = os.system( 'python -c "import ws4py;print ws4py.__version__"' )
        if ( version != 0 ):
            print ""
            print "ERROR......INSTALLATION OF ws4py HAS FAILED"
            print ""
            exit()
    else:
        print ""
        print "ws4py already installed.....moving on to next installation"
        print ""

    #------------------------------------------------------------------------------------
    #If all of the installations were successful, telling user installation was successful

    print "Installation was successful....."
    print ""


#Calling the install method which installs the dependencies
install()
