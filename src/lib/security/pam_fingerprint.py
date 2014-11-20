"""
pamfingerprint
PAM implementation.

Copyright 2014 Philipp Meisberger, Bastian Raschke.
All rights reserved.
"""

import sys
sys.path.append('/usr/lib')

from pamfingerprint.version import VERSION
from pamfingerprint.Config import *

from PyFingerprint.PyFingerprint import *

import hashlib
import syslog


def pam_sm_authenticate(pamh, flags, argv):
    """
    PAM service function for user authentication.

    @param pamh
    @param flags
    @param argv
    @return integer
    """

    ## Tries to get user which is asking for permission
    try:
        userName = pamh.ruser

        ## Fallback
        if ( userName == None ):
            userName = pamh.get_user()

        ## Be sure the user is set
        if ( userName == None ):
            raise Exception('The user is not known!')

    except:
        e = sys.exc_info()[1]
        syslog.syslog(syslog.LOG_ERR, e.message)
        return pamh.PAM_USER_UNKNOWN

    ## Tries to init Config
    try:
        config = Config('/etc/pamfingerprint.conf')

    except:
        e = sys.exc_info()[1]
        syslog.syslog(syslog.LOG_ERR, e.message)
        return pamh.PAM_IGNORE

    syslog.syslog(syslog.LOG_INFO, 'The user "' + userName + '" is asking for permission for service "' + str(pamh.service) + '".')

    ## Checks if the the user was added in configuration
    if ( config.itemExists('Users', userName) == False ):
        syslog.syslog(syslog.LOG_ERR, 'The user was not added!')
        return pamh.PAM_IGNORE

    ## Tries to get user information (template position, fingerprint hash)
    try:
        userData = config.readList('Users', userName)

        ## Validates user information
        if ( len(userData) != 2 ):
            raise Exception('The user information of "' + userName + '" is invalid!')

        expectedPositionNumber = int(userData[0])
        expectedFingerprintHash = userData[1]

    except:
        e = sys.exc_info()[1]
        syslog.syslog(syslog.LOG_ERR, e.message)
        return pamh.PAM_AUTH_ERR

    ## Gets sensor connection values
    port = config.readString('PyFingerprint', 'port')
    baudRate = config.readInteger('PyFingerprint', 'baudRate')
    address = config.readHex('PyFingerprint', 'address')
    password = config.readHex('PyFingerprint', 'password')

    ## Tries to init PyFingerprint
    try:
        fingerprint = PyFingerprint(port, baudRate, address, password)

        if ( fingerprint.verifyPassword() == False ):
            raise ValueError('The given fingerprint sensor password is wrong!')

    except:
        syslog.syslog(syslog.LOG_ERR, 'The fingerprint sensor could not be initialized!')
        pamh.conversation(pamh.Message(pamh.PAM_TEXT_INFO, 'pamfingerprint ' + VERSION + ': Sensor initialization failed!'))
        return pamh.PAM_IGNORE

    msg = pamh.Message(pamh.PAM_TEXT_INFO, 'pamfingerprint ' + VERSION + ': Waiting for finger...')
    pamh.conversation(msg)

    ## Tries to read fingerprint
    try:
        while ( fingerprint.readImage() == False ):
            pass

        fingerprint.convertImage(0x01)

        ## Gets position of template
        result = fingerprint.searchTemplate()
        positionNumber = result[0]

        ## Checks if the template position is invalid
        if ( positionNumber == -1 ):
            raise Exception('No match found!')

        ## Checks if the template position is correct
        if ( positionNumber != expectedPositionNumber ):
            raise Exception('The template position of the found match is not equal to the stored one!')

        ## Gets characteristics
        fingerprint.loadTemplate(positionNumber, 0x01)
        characterics = fingerprint.downloadCharacteristics(0x01)

        ## Calculates hash of template
        fingerprintHash = hashlib.sha256(str(characterics)).hexdigest()

        ## Checks if the calculated hash is equal to expected hash from user
        if ( fingerprintHash == expectedFingerprintHash ):
            syslog.syslog(syslog.LOG_INFO, 'Access granted!')
            pamh.conversation(pamh.Message(pamh.PAM_TEXT_INFO, 'pamfingerprint ' + VERSION + ': Access granted!'))
            return pamh.PAM_SUCCESS
        else:
            syslog.syslog(syslog.LOG_WARNING, 'The found match is not assigned to user!')
            pamh.conversation(pamh.Message(pamh.PAM_TEXT_INFO, 'pamfingerprint ' + VERSION + ': Access denied!'))
            return pamh.PAM_AUTH_ERR

    except:
        e = sys.exc_info()[1]
        syslog.syslog(syslog.LOG_ERR, 'Fingerprint read failed!')
        pamh.conversation(pamh.Message(pamh.PAM_TEXT_INFO, 'pamfingerprint ' + VERSION + ': Access denied!'))
        return pamh.PAM_AUTH_ERR

    ## Denies for default
    return pamh.PAM_AUTH_ERR


def pam_sm_setcred(pamh, flags, argv):
    """
    PAM service function to alter credentials.

    @param pamh
    @param flags
    @param argv
    @return integer
    """

    return pamh.PAM_SUCCESS
