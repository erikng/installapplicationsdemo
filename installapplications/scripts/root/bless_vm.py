#!/Library/installapplications/Python.framework/Versions/Current/bin/python3
'''Bless a Virtual Machine'''

# This script blesses the booted volume on 10.13+ APFS volumes for virtual
# machines. This is due to either a bug in macOS or virtual machine tools
# like VMware Fusion that causes the device to become unable to boot after
# enabling FileVault.

# This script makes many assumptions about the boot volume and has been tested
# with common vfuse configurations. Your mileage may vary.

# Written by Erik Gomez.
# sysctl function written by Michael Lynn.

from ctypes import CDLL, c_uint, byref, create_string_buffer
from ctypes.util import find_library
import platform
import plistlib
import subprocess


def deplog(text):
    '''Add a line to the depnotify file'''
    depnotify = "/private/var/tmp/depnotify.log"
    with open(depnotify, "a+") as log:
        log.write(text + "\n")


def get_os_version():
    '''Return OS version.'''
    return platform.mac_ver()[0]


def sysctl(name):
    '''Wrapper for sysctl so we don't have to use subprocess'''
    size = c_uint(0)
    # Find out how big our buffer will be
    libc = CDLL(find_library('c'))
    libc.sysctlbyname(name, None, byref(size), None, 0)
    # Make the buffer
    buf = create_string_buffer(size.value)
    # Re-run, but provide the buffer
    libc.sysctlbyname(name, buf, byref(size), None, 0)
    return buf.value


def is_virtual_machine():
    '''Returns True if this is a VM, False otherwise'''
    cpu_features = sysctl('machdep.cpu.features').split()
    return 'VMM' in cpu_features


def get_machine_type():
    '''Return the machine type: physical, vmware, virtualbox, parallels or
    unknown_virtual'''
    vm_type = 'physical'
    if not is_virtual_machine():
        return vm_type

    # this is a virtual machine; see if we can tell which vendor
    try:
        proc = subprocess.Popen(['/usr/sbin/system_profiler', '-xml',
                                 'SPEthernetDataType', 'SPHardwareDataType'],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = proc.communicate()[0]
        plist = plistlib.loads(output)
        br_version = plist[1]['_items'][0]['boot_rom_version']

        if 'VMW' in br_version:
            vm_type = 'vmware'
        elif 'VirtualBox' in br_version:
            vm_type = 'virtualbox'
        else:
            ethernet_vid = plist[0]['_items'][0]['spethernet_vendor-id']
            if '0x1ab8' in ethernet_vid:
                vm_type = 'parallels'

        return vm_type

    except (IOError, KeyError, OSError):
        pass

    return 'physical'


def bless(path):
    # pylint: disable=broad-except
    '''Bless a folder path'''
    try:
        blesscmd = ['/usr/sbin/bless', '--folder', path, '--setBoot']
        proc = subprocess.Popen(blesscmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        output = proc.communicate()[0]
        return output
    except BaseException:
        return None
    # pylint: enable=broad-except


def get_filesystem_type(path):
    '''Get the file system type'''
    filetype = ''
    try:
        diskutilcmd = ['/usr/sbin/diskutil', 'info', '-plist', path]
        proc = subprocess.Popen(diskutilcmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        output, _ = proc.communicate()
    except (IOError, OSError):
        output = None
    if output:
        outplist = plistlib.loads(output.strip())
        filetype = outplist.get('FilesystemType', '')
    return filetype


def main():
    '''Main thread'''
    if ('10.13' or '10.14' or '10.15' in get_os_version() and 'apfs' in get_filesystem_type('/') and
            get_machine_type() != 'physical'):
        deplog("Status: Configurating Virtual Machine for encryption technology...")
        bless('/Volumes/Macintosh HD/System/Library/CoreServices')


if __name__ == '__main__':
    main()
