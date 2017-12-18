#!/usr/bin/python
import subprocess
import os


def launchctld(identifier):
    launchd = identifier + '.plist'
    try:
        path = os.path.join('/Library', 'LaunchDaemons', launchd)
        cmd = ['/bin/launchctl', 'load', path]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        output, err = proc.communicate()
        return output
    except KeyError:
        pass


def main():
    launchctld('com.googlecode.munki.managedsoftwareupdate-check')
    launchctld('com.googlecode.munki.managedsoftwareupdate-install')
    launchctld('com.googlecode.munki.managedsoftwareupdate-manualcheck')
    launchctld('com.googlecode.munki.logouthelper')


if __name__ == '__main__':
    main()
