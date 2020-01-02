#!/Library/installapplications/Python.framework/Versions/3.8/bin/python3
'''Munki LaunchDaemon loading demo example'''

# A simple python function for loading munki's launchd items without
# needing to reboot the machine.

# Written by Erik Gomez

import subprocess
import os


def launchctld(identifier):
    '''Load a launchdaemon with the identifier specified'''
    launchd = identifier + '.plist'
    try:
        path = os.path.join('/Library/LaunchDaemons', launchd)
        cmd = ['/bin/launchctl', 'load', path]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        output = proc.communicate()[0]
        return output
    except KeyError:
        pass


def main():
    '''Main thread'''
    launchctld('com.googlecode.munki.managedsoftwareupdate-check')
    launchctld('com.googlecode.munki.managedsoftwareupdate-install')
    launchctld('com.googlecode.munki.managedsoftwareupdate-manualcheck')
    launchctld('com.googlecode.munki.logouthelper')


if __name__ == '__main__':
    main()
