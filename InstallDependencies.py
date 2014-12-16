#This file will automatically install all of the dependencies for the BlocklyPropClient

import os

#This method will install and test the dependencies
def install():
    print "Beginning installation....."
    print ""
    
    #Installing CherryPy
    os.chdir( "dependencies/CherryPy/" )
    os.system( "python setup.py install" )
    
    print ""
    print "CherryPy installation complete"
    print ""
    
    #Installing PySerial
    os.chdir( "../pyserial" )
    os.system( "python setup.py install" )

    print ""
    print "PySerial installation complete"
    print ""
    
    #Installing ws4py
    os.chdir( "../ws4py" )
    os.system( "python setup.py install" )
    
    print ""
    print "ws4py installation complete"
    print ""

    #--------------------------------------------------------------------------------------
    
    #Testing whether installation was successful for each dependency

    #Testing whether CherryPy was installed correctly
    version = os.system( 'python -c "import cherrypy;print cherrypy.__version__"' )
    if ( version != 0 ):
        print ""
        print "ERROR......INSTALLATION OF CherryPy HAS FAILED"
        print ""
        exit()

    version = os.system( 'python -c "import serial;print serial.Serial()"' )
    if ( version != 0 ):
        print ""
        print "ERROR......INSTALLATION OF PySerial HAS FAILED"
        print ""
        exit()

    version = os.system( 'python -c "import ws4py;print ws4py.__version__"' )
    if ( version != 0 ):
        print ""
        print "ERROR......INSTALLATION OF ws4py HAS FAILED"
        print ""
        exit()

    print ""
    print "Installation was successful....."
    print ""


#Calling the install method which installs the dependencies
install()