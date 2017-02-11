#!/bin/sh --
#
# The purpose of this script is to create a signed Mac OS X deployment package
# The package will be created as ./|APP_NAME|-|VERSION|-MacOS.pkg
#
# Requirements for this script are:
#
#   User must specify the application bundle name without extension: (example -a "MyApplication")
#   User must specify the package version: (example: "-v 0.9.66")
#   All other parameters are optional: (restart requirement, developer identity, is this a deployment package)
#
#   These files/folders must exist (in relation to this script's folder):
#      ../drivers/FTDIUSBSerialDriver.kext
#      ../dist/|APP_NAME|.app
#   To update the driver, 
#      - download from and install driver (from http://www.ftdichip.com/Drivers/VCP.htm)
#        - select the currently supported Mac OS X VCP driver from that page (i.e. x64 (64-bit))
#        - or use: http://www.ftdichip.com/Drivers/VCP/MacOSX/FTDIUSBSerialDriver_v2_3.dmg
#        - install FTDI's driver package onto the development Mac OS X system
#      - copy the FTDIUSBSerialDriver.kext from /Library/Extensions/ to the ../drivers/ folder
#   The |APP_NAME|.app release must be:
#       - digitally signed with ./macappcodesign.sh, to sign the app with an "identified developer" ID and checksum
#       - stored in the ../dist/ folder
#

usage()
{
cat << EOF
Usage: $0 options

This script builds a signed installation package.

OPTIONS:
    -h  show usage
    -a  application bundle name
        - example: -a "MyApplication"
    -r  require restart after installation (applies only if FTDIUSBSerialDriver is included)
    -f  include FTDIUSBSerialDriver in the package
    -s  developer identity certificate key
        - example: -s "Developer Identity" (default is "Developer ID Installer")
    -v  version
        - example: -v 0.9.66 (required parameter)
    -d  use deployment identifier (default is: com.test.ParallaxInc, deploy is: com.ParallaxInc.|APP_NAME|)

    example: ./macsignedpack.sh -r -f -s "Developer ID Installer" -v 0.9.66 -d

EOF
}

#
# Resource paths
#
RESOURCES="./mac-resources/"
DISTRIBUTION="../dist/"

#
# Default installation locations
#
# note: the FTDI kext used to be in "/System/Library/Extensions/" per Apple's previous suggestion (before Mavericks?)
FTDIDRIVER_DEST_DIR="/Library/Extensions/"
DEFAULT_APP_DIR="/Applications/"

#
# Default component names
#
FTDIDRIVER=FTDIUSBSerialDriver
FTDIDRIVER_KEXT=${FTDIDRIVER}.kext

#
# Modified temporary distro xml
#
# note: will contain copied or sed-modified version of template DistributionXXXX.xml
DIST_DST=DistributionMOD.xml

#
# initialize input options with default values
#
APP_NAME=
VERSION=
IDENTITY="Developer ID Installer"
REQUIRE_RESTART_TEXT="requireRestart"
RESTART=false
DEPLOY=false
FTDI=false

#
# get parms as flags or as requiring arguments
#
while getopts "ha:rfs:dv:" OPTION
do
    case $OPTION in
        h)
            usage; exit 1 ;;
        a)
            APP_NAME=$OPTARG
            ;;           
        r)
            if [[ $OPTARG =~ ^[0-9]+$ ]]
            then
                RESTART=$OPTARG
            elif [[ $OPTARG =~ ^-, ]]
            then
                RESTART=true
                let OPTIND=$OPTIND-1
            else
                RESTART=true
            fi
            ;;
        f)
            if [[ $OPTARG =~ ^[0-9]+$ ]]
            then
                FTDI=$OPTARG
            elif [[ $OPTARG =~ ^-, ]]
            then
                FTDI=true
                let OPTIND=$OPTIND-1
            else
                FTDI=true
            fi
            ;;
        s)
            IDENTITY=$OPTARG
            ;;
        d)
            if [[ $OPTARG =~ ^[0-9]+$ ]]
            then
                DEPLOY=$OPTARG
            elif [[ $OPTARG =~ ^-, ]]
            then
                DEPLOY=true
                let OPTIND=$OPTIND-1
            else
                DEPLOY=true
            fi
            ;;
        v)
            VERSION=$OPTARG
            ;;
        ?)
            echo "[HALT] Misconfigured options - see usage notes"
            usage; exit  ;;
    esac
done

#
# Error if no application bundle name (-a bundle) was declared
#
if [[ -z $APP_NAME ]]
then
    echo "[HALT] No application bundle was declared - see usage notes for -a."
    echo
    usage
    exit 1
fi

#
# Set bundle name
#
APP_BUNDLE=${APP_NAME}.app

#
# Error if no version (-v) option declared
#
if [[ -z $VERSION ]]
then
    echo "[HALT] No version option was declared - see usage notes for -v."
    echo
    usage
    exit 1
fi

#
# Error if no version string declared
#
if [ ${VERSION}X == X ]
then
    echo "[HALT] No version string was declared - see usage notes for -v."
    echo
    usage
    exit 1
fi

# Show Info
echo "[INFO] Processing target: \"${DISTRIBUTION}${APP_NAME}.app\""
echo "[INFO] As build version: \"${VERSION}\""
echo "[INFO] Using identity: \"${IDENTITY}\""

#
# Verify that app is code-signed
# A properly signed app will contain a _CodeSignature directory and CodeResource file
#
echo "Validating application..."
if [[ -e ${DISTRIBUTION}${APP_BUNDLE} ]]
then
    #
    # Found bundle
    #
    if [[ -e ${DISTRIBUTION}${APP_BUNDLE}/Contents/_CodeSignature/CodeResources ]]
    then
        #
        # Found code signature, now we'll check validity
        # A single "-v" == "verify app signing", gives no result on valid app signing 
        #
        codesign -v ${DISTRIBUTION}${APP_BUNDLE}
        if [ "$?" != "0" ]; then
            echo "  [Error] Application signature is invalid!" 1>&2
            exit 1
        else
            echo "  Verified ${DISTRIBUTION}${APP_BUNDLE} signature"
        fi
    else
        echo "  [Error] Application bundle is not signed."
        exit 1
    fi
fi

exit

#
# Use security utility to determine if the developer installation identity is valid
#
echo "Validating developer identity certificate..."
SECUREID=`security find-certificate -c "$IDENTITY" | grep labl`
if [[ -n ${SECUREID} ]]
then
    echo "  Found identity: \"${IDENTITY}\""
else
    echo "  [Error] Identity: \"${IDENTITY}\" does not exist!"
    echo "          Use Keychain Access app to verify that you are using an authorized developer installation certificate..."
    echo "          i.e. search within Login Keychain 'My Certificates' Category for 'Developer ID Installer' certificate."
    echo
    exit 1
fi
echo

#
# Does the installation require a restart?
#
if [[ $RESTART == true ]]
then
    echo "[INFO] Restart required after installation"
else
    echo "[INFO] Restart NOT required after installation"
fi

#
# Developer PARALLAX_IDENTIFIER & FTDI_IDENTIFIER (package can be for testing or deployment)
#
if [[ $DEPLOY == true ]]
then
    PARALLAX_IDENTIFIER=com.ParallaxInc
    #   Will get modified to: "com.ParallaxInc.|APP_NAME|" below
    FTDI_IDENTIFIER=com.FTDI.driver
    #   Will get modified to: "com.FTDI.driver.FTDIUSBSerialDriver" below
    echo "OPT: Package CFBundleIdentifiers will be set for deployment"
else
    PARALLAX_IDENTIFIER=com.test.ParallaxInc
    #   Will get modified to: "com.test.ParallaxInc.|APP_NAME|" below
    FTDI_IDENTIFIER=com.test.FTDI.driver
    #   Will get modified to: "com.test.FTDI.driver.FTDIUSBSerialDriver" below
    echo "OPT: Package CFBundleIdentifiers will be set for testing"
fi

#
# touch the entire content of the current directory to set most-recent mod dates
#
touch *

#
# Build the FTDIUSBSerialDriver.kext component package
#
# Include FTDI in the Installer package?
if [[ ${FTDI} == true ]]
then
    echo "[INFO] FTDI kext WILL BE included in this packag"
#
#   is the FTDI Driver kext available?
    if [[ -e ../drivers/${FTDIDRIVER_KEXT} ]]
    then
        echo "  Found FTDI USB Serial Driver"
        DIST_SRC=DistributionFTDI.xml
#
#       build the FTDI Driver component package
        echo; echo "  Building FTDI USB Driver package..."
        pkgbuild    --root ../drivers/${FTDIDRIVER_KEXT} \
                    --identifier ${FTDI_IDENTIFIER}.${FTDIDRIVER} \
                    --timestamp \
                    --install-location ${FTDIDRIVER_DEST_DIR}${FTDIDRIVER_KEXT} \
                    --sign "$IDENTITY" \
                    --version ${VERSION} \
                    ${DISTRIBUTION}FTDIUSBSerialDriver.pkg
    else
        echo "  [Error] FTDI USB Serial driver missing. Please read $0 comments."
        exit 1
    fi
else
    echo "[INFO] FTDI kext WILL NOT BE installed by this package"
    DIST_SRC=Distribution.xml
fi

#
# Build the application component package
#
echo; echo "Building Application package..."
pkgbuild --root ${DISTRIBUTION}${APP_BUNDLE} \
	 --identifier ${PARALLAX_IDENTIFIER}.${APP_NAME} \ 
	 --timestamp \
	 --install-location ${DEFAULT_APP_DIR}${APP_BUNDLE} \
         --sign "$IDENTITY" \
	 --version ${VERSION} \
         ${APP_NAME}.pkg

#
# Write a synthesized distribution xml directly (NO LONGER USED, BUT CAN PROVIDE A DISTRIBUTION XML FILE AS A TEMPLATE)
#
#productbuild --synthesize --sign "$IDENTITY" --timestamp=none --package ${APP_NAME}.pkg --package FTDIUSBSerialDriver.pkg ${RESOURCES}${DIST_SRC}
#

#
# Modify the existing DistributionXXXX.xml only if requiredRestart is requested
#
if [[ ${FTDI} == true ]]
then
    if [[ ${RESTART} == true ]]
    then
	echo "Modifying distribution xml to require restart..."
        sed "s/\"none\"\>FTDI/\"${REQUIRE_RESTART_TEXT}\"\>FTDI/g" ${RESOURCES}${DIST_SRC} > ${RESOURCES}${DIST_DST}
    else
        cat ${RESOURCES}${DIST_SRC} > ${RESOURCES}${DIST_DST}
    fi
else
    cat ${RESOURCES}${DIST_SRC} > ${RESOURCES}${DIST_DST}
fi

#
# Build the Product Installation Package
#
# note: $DIST_DST holds a copied or modified version of one of the 2 DistributionXXXX.xml files
#       The $DIST_DST contains installation options & links to resources for the product package
echo; echo "Building product package..."
productbuild    --distribution ${RESOURCES}${DIST_DST} \
                --resources ${RESOURCES} \
                --timestamp \
                --version $VERSION \
                --package-path ./ \
                --sign "$IDENTITY" \
                ./${APP_NAME}-${VERSION}-MacOS.pkg

if [[ -e ${RESOURCES}${DIST_DST} ]]
then
    echo
    echo "Cleaning up temporary files..."   
    rm ${RESOURCES}${DIST_DST}
fi

echo; echo "Done!"
exit 0
