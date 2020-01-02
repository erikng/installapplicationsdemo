#!/Library/installapplications/Python.framework/Versions/3.8/bin/python3
'''DEPNotify customization demo code'''
# -*- coding: utf-8 -*-

# A simple python function for writing to DEPNotify's log file.
# In order to pass more complex strings, you must use r"TEXT". r tells python
# to pass the literal string vs an interpreted string.

# Written by Erik Gomez
import os


def deplog(text):
    '''Simple function to pass to DEPNotify log'''
    depnotify = "/private/var/tmp/depnotify.log"
    with open(depnotify, "a+") as log:
        log.write(text + "\n")


def main():
    '''Main thread'''
    depnotify_log = '/private/var/tmp/depnotify.log'
    if os.path.exists(depnotify_log):
        # pylint: disable=bare-except
        try:
            os.remove(depnotify_log)
        except:
            pass
        # pylint: enable=bare-except
    deplog("Command: WindowTitle: InstallApplications Demo")
    deplog("Command: Image: /Applications/Launchpad.app/Contents/Resources/Launchpad.icns")
    deplog("Status: Configuring Machine..")


if __name__ == '__main__':
    main()
