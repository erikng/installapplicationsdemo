#!/Library/installapplications/Python.framework/Versions/Current/bin/python3
'''Caffeinate example script'''

# This example script uses the caffeine command to ensure the machine never
# goes to sleep. You should be very careful with this script if you call it
# from another script as it will more than likely pause your entire workflow
# until the caffeination is over. InstallApplications can handle this by
# passing the "donotwait" key in the json payload.

# Written by Erik Gomez

import subprocess


def deplog(text):
    '''Add a line to the depnotify file'''
    depnotify = "/private/var/tmp/depnotify.log"
    with open(depnotify, "a+") as log:
        log.write(text + "\n")


def main():
    # pylint: disable=broad-except
    '''Main thread'''
    caffeinationtime = '600'  # amount in seconds
    caffeinatecmd = ['/usr/bin/caffeinate', '-dimut', caffeinationtime]
    try:
        subprocess.Popen(caffeinatecmd)
        deplog("Status: Caffeinating machine...")
    except BaseException:
        print('Could not caffeinate machine')
    # pylint: enable=broad-except


if __name__ == '__main__':
    main()
