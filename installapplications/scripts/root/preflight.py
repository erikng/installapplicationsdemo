#!/Library/installapplications/Python.framework/Versions/Current/bin/python3
'''Preflight demo script'''

# A simple example to run a preflight or not if InstallApplications has ever ran
# on the machine prior. You probably wouldn't want to do something like this in
# production.

# Written by Erik Gomez

import plistlib
import subprocess
import sys
from distutils.version import LooseVersion


def get_install_package_version(pkgid):
# pylint: disable=broad-except
    """
    Checks a package id against the receipts to
    determine if a package is already installed.
    Returns the version string of the installed pkg
    if it exists, or an empty string if it does not
    """

    # First check (Leopard and later) package database
    proc = subprocess.Popen(['/usr/sbin/pkgutil',
                             '--pkg-info-plist', pkgid],
                            bufsize=1,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    (out, dummy_err) = proc.communicate()

    if out:
        try:
            plist = plistlib.loads(out)
        except Exception:
            found_version = '0.0.0.0.0'
        else:
            found_version = plist.get('pkg-version', '0.0.0.0.0')
    else:
        found_version = '0.0.0.0.0'

    return found_version
# pylint: enable=broad-except


def main():
    '''If the main thread exit(0), then all of our checks have completed, and
    there is no need to run InstallApplications again. Should any of these checks
    fail though, we need to re-run the provisioning process.'''

    pkg_version = LooseVersion(str(get_install_package_version(
        'menu.nomad.DEPNotify')))

    if pkg_version >= LooseVersion('1.1.6'):
        pass
    else:
        sys.exit(1)

    print('All checks passed!')
    sys.exit(0)


if __name__ == '__main__':
    main()
