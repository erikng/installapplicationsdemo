#!/Library/installapplications/Python.framework/Versions/Current/bin/python3
'''DEPNotify end demo code'''
# -*- coding: utf-8 -*-

# A simple python function for writing to DEPNotify's log file.
# In order to pass more complex strings, you must use r"TEXT". r tells python
# to pass the literal string vs an interpreted string.

# Written by Erik Gomez


def deplog(text):
    '''Add a line to the depnotify file'''
    depnotify = "/private/var/tmp/depnotify.log"
    with open(depnotify, "a+") as log:
        log.write(text + "\n")


def main():
    '''Main thread'''
    deplog("Status: Machine is configured!")
    deplog('Command: Logout: Please logout now to start the disk encryption.')


if __name__ == '__main__':
    main()
