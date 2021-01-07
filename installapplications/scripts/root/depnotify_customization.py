#!/Library/installapplications/Python.framework/Versions/Current/bin/python3
'''DEPNotify customization demo code'''
# -*- coding: utf-8 -*-

# A simple python function for writing to DEPNotify's log file.
# In order to pass more complex strings, you must use r"TEXT". r tells python
# to pass the literal string vs an interpreted string.

# Written by Erik Gomez
import os
import platform
import time


def deplog(text):
    '''Simple function to pass to DEPNotify log'''
    depnotify = "/private/var/tmp/depnotify.log"
    with open(depnotify, "a+") as log:
        log.write(text + "\n")


def get_os_version():
    '''Return OS version.'''
    return platform.mac_ver()[0]


def main():
    '''Main thread'''
    depnotify_log = '/private/var/tmp/depnotify.log'
    # 10.15 has a new path for all built-in apps except for Safari
    if '10.15' in get_os_version():
        icns_path = '/System/Applications/Launchpad.app/Contents/Resources/Launchpad.icns'
    else:
        icns_path = '/Applications/Launchpad.app/Contents/Resources/Launchpad.icns'
    if os.path.exists(depnotify_log):
        # pylint: disable=bare-except
        try:
            os.remove(depnotify_log)
        except:
            pass
        # pylint: enable=bare-except
    deplog("Command: WindowTitle: InstallApplications Demo")
    deplog("Command: Image: {}".format(icns_path))
    deplog("Status: Configuring Machine...")

    time.sleep(2)


if __name__ == '__main__':
    main()
