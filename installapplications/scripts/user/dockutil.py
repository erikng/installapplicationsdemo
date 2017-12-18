#!/usr/bin/python

# python wrapper for dockutil. We use the --no-restart flag for most of this
# to reduce the amount of flashes (to one) that occur on the user's desktop.

# Written by Erik Gomez

import os
import subprocess


def dockutil(type, itempath, norestart):
    if norestart is True:
        cmd = ['/usr/local/bin/dockutil', type, itempath, '--no-restart']
    else:
        cmd = ['/usr/local/bin/dockutil', type, itempath]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        output, err = proc.communicate()
        return output
    except Exception:
        return None


def dockutilFolder(type, itempath, norestart, sorttype):
    if norestart is True:
        cmd = ['/usr/local/bin/dockutil', type, itempath, '--sort', sorttype,
               '--no-restart']
    else:
        cmd = ['/usr/local/bin/dockutil', type, itempath, '--sort', sorttype]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        output, err = proc.communicate()
        return output
    except Exception:
        return None


def main():
    # Remove all dock items.
    dockutil('--remove', 'all', True)

    # Add the paths of the items you want to add to the dock here.
    applist = [
        '/Applications/Safari.app',
        '/Applications/Managed Software Center.app',
        '/Applications/System Preferences.app'
    ]
    for itempath in applist:
        if os.path.isdir(itempath):
            dockutil('--add', itempath, True)

    # Tell dockutil to restart and finally update the dock.
    dockutilFolder('--add', '/Applications', False, 'name')


if __name__ == '__main__':
    main()
