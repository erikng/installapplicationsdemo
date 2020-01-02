#!/Library/installapplications/Python.framework/Versions/3.8/bin/python3
'''Munki Auto trigger python example code'''

# This script uses managedsoftwareupdate binary to run an auto run, which
# mimics the launch daemon. This ensures a machine is fully compliant after
# your DEP run. You should be very careful with this script if you call it from
# another script as it will more than likely pause your entire workflow until
# the munki run is over. InstallApplications can handle this by passing the
# "donotwait" key in the json payload.

# You _must_ pass preexec_fn=os.setpgrp in the subprocess, otherwise when
# your original script exits, it will kill the munki run. This is because
# preexec_fn=os.setpgrp changes the SIGINT of this child process (this script)
# would usually receive, thereby allowing it to continue to process even if the
# original parent has sent a SIGINT to it's own child processes.

# Written by Erik Gomez

import os
import subprocess


def main():
    # pylint: disable=broad-except
    # pylint: disable=subprocess-popen-preexec-fn
    '''Main thread'''
    munkicheckcmd = ['/usr/local/munki/managedsoftwareupdate', '--auto']
    try:
        subprocess.Popen(munkicheckcmd, preexec_fn=os.setpgrp)
    except BaseException:
        print('Could not trigger auto munki run')
    # pylint: enable=broad-except
    # pylint: enable=subprocess-popen-preexec-fn


if __name__ == '__main__':
    main()
