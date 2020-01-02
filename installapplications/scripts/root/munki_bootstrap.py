#!/Library/installapplications/Python.framework/Versions/3.8/bin/python3
'''Munki bootstrap demo code'''

# This script is used to bootstrap munki from a root process.
# Rather than rely on mobileconfigs (that may come from other systems), some
# basic defaults are created.

# To speed up the DEP run, an --id run is used in conjunction with
# --munkipkgsonly. This ensures apple updates (which may require a reboot)
# aren't processed.

# An --applesuspkgsonly function is provided, though it's recommended you run
# the munki_auto_trigger.py script (found in this repo) at the end of your
# DEP run.

# Finally a fake null value is sent to munki's preference for LastCheckDate.
# Using this in conjuction with the yo_action_example.py script will cause
# Managed Software Center to immediately check for an update when it's first
# opened.

# Written by Erik Gomez.

import subprocess
# pylint: disable=import-error
from Foundation import (CFPreferencesSetValue, kCFPreferencesAnyUser,
                        kCFPreferencesCurrentHost)
# pylint: enable=import-error


def munkirun(identifier):
    # pylint: disable=broad-except
    '''Only download munki pkgs via a specific manifest'''
    try:
        cmd = ['/usr/local/munki/managedsoftwareupdate', '--id', identifier,
               '--munkipkgsonly']
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        output = proc.communicate()[0]
        return output
    except BaseException:
        return None
    # pylint: enable=broad-except


def munkiinstall():
    # pylint: disable=broad-except
    '''Only install munki pkgs'''
    try:
        cmd = ['/usr/local/munki/managedsoftwareupdate', '--installonly']
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        output = proc.communicate()[0]
        return output
    except BaseException:
        return None
    # pylint: enable=broad-except


def munkiappleupdates():
    # pylint: disable=broad-except
    '''Download apple updates only'''
    try:
        cmd = ['/usr/local/munki/managedsoftwareupdate', '--applesuspkgsonly']
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        output = proc.communicate()[0]
        return output
    except BaseException:
        return None
    # pylint: enable=broad-except


def main():
    '''Main thread'''
    # pylint: disable=line-too-long
    munkiurl = 'https://raw.githubusercontent.com/erikng/installapplicationsdemo/python3/munki'
    # pylint: enable=line-too-long
    backupmanifest = 'production'

    # Set basic munki preferences
    CFPreferencesSetValue(
        'InstallAppleSoftwareUpdates', True,
        '/Library/Preferences/ManagedInstalls',
        kCFPreferencesAnyUser, kCFPreferencesCurrentHost)

    CFPreferencesSetValue(
        'SoftwareRepoURL', munkiurl,
        '/Library/Preferences/ManagedInstalls',
        kCFPreferencesAnyUser, kCFPreferencesCurrentHost)

    CFPreferencesSetValue(
        'ClientIdentifier', backupmanifest,
        '/Library/Preferences/ManagedInstalls',
        kCFPreferencesAnyUser, kCFPreferencesCurrentHost)

    # Run Munki with manifest you want to use
    munkirun('depdemo')

    # Install downloaded packages
    munkiinstall()

    CFPreferencesSetValue(
        'LastCheckDate', '',
        '/Library/Preferences/ManagedInstalls',
        kCFPreferencesAnyUser, kCFPreferencesCurrentHost)


if __name__ == '__main__':
    main()
