#!/Library/installapplications/Python.framework/Versions/Current/bin/python3
'''dockutil wrapper'''

# Python wrapper for dockutil. We use the --no-restart flag for most of this
# to reduce the amount of flashes (to one) that occur on the user's desktop.

# This script only runs if the items expected are either found or not found.

# Written by Erik Gomez

import os
import platform
import subprocess
import sys


def hello_install_file(path):
    '''Create a file that hello is looking for to determine install status'''
    with open(path, "a+") as log:
        log.write("installed")


def dockutil(itemtype, itempath, norestart):
    '''setup an item'''
    if norestart is True:
        cmd = ['/Library/installapplications/Python.framework/Versions/3.8/bin/python3',
               '/Library/installapplications/dockutil',
               itemtype, itempath, '--no-restart']
    else:
        cmd = ['/Library/installapplications/Python.framework/Versions/3.8/bin/python3',
               '/Library/installapplications/dockutil',
               itemtype, itempath]
    try:
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = proc.communicate()[0]
        return output
    # pylint: disable=broad-except
    except Exception:
        return None


def dockutil_upgrade(itemtype, itempath, olditem, norestart):
    '''uprade an item'''
    if norestart is True:
        cmd = ['/Library/installapplications/Python.framework/Versions/3.8/bin/python3',
               '/Library/installapplications/dockutil',
               itemtype, itempath, '--replacing', olditem, '--no-restart']
    else:
        cmd = ['/Library/installapplications/Python.framework/Versions/3.8/bin/python3',
               '/Library/installapplications/dockutil',
               itemtype, itempath, '--replacing', olditem]
    try:
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = proc.communicate()[0]
        return output
    # pylint: disable=broad-except
    except Exception:
        return None


def dockutil_folder(itemtype, itempath, norestart, sorttype):
    '''set a folder'''
    if norestart is True:
        cmd = ['/Library/installapplications/Python.framework/Versions/3.8/bin/python3',
               '/Library/installapplications/dockutil',
               itemtype, itempath, '--sort', sorttype, '--no-restart']
    else:
        cmd = ['/Library/installapplications/Python.framework/Versions/3.8/bin/python3',
               '/Library/installapplications/dockutil',
               itemtype, itempath, '--sort', sorttype]
    try:
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = proc.communicate()[0]
        return output
    # pylint: disable=broad-except
    except Exception:
        return None


def get_os_version():
    '''Return OS version.'''
    return platform.mac_ver()[0]


def main():
    '''Main thread'''
    # Replace the dock if it still the Apple default.
    if (b'was not found in' in dockutil('--find', 'Google Chrome', True)
            and b'was found in' in dockutil('--find', 'Safari', True)
            and b'was not found in' in dockutil('--find', 'Managed Software Center', True)
            and b'was found in' in dockutil('--find', 'System Preferences', True)):
        print('Detected unprovisioned dock, fixing.')

        # Remove all dock items
        dockutil('--remove', 'all', True)

        # Add the ones we care about, but only if they exist
        applist = [
            '/Applications/Google Chrome.app',
            '/Applications/Safari.app',
            '/Applications/Managed Software Center.app'
        ]
        # 10.15 has a new path for all built-in apps except for Safari
        if '10.15' in get_os_version():
            applist.append('/System/Applications/System Preferences.app')
        else:
            applist.append('/Applications/System Preferences.app')

        # Loop through the apps and add them to the dock if they are present
        # on disk
        for itempath in applist:
            if os.path.isdir(itempath):
                dockutil('--add', itempath, True)

        # Somewhat of a hack to force dock refresh at the end and not cause
        # multiple flashes.
        dockutil('--remove', 'Applications', True)
        dockutil_folder('--add', '/Applications', False, 'name')
        hello_install_file('/var/tmp/dockutil.complete')
    else:
        print('Detected previoiusly provisioned dock, exiting.', file=sys.stderr)
        hello_install_file('/var/tmp/dockutil.complete')


if __name__ == '__main__':
    main()
