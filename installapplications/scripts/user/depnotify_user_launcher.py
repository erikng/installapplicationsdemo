#!/Library/installapplications/Python.framework/Versions/3.8/bin/python3
'''dockutil wrapper'''

# Written by Erik Gomez
# Lots of ideas taken from dockutil and munki

# It should really be rewritten, but it works for now and is more stable
# than the built in method offered by InstallApplications

import os
import platform
import plistlib
import subprocess
import tempfile
import time


def get_macos_version():
    '''returns a tuple with the (major,minor,revision) numbers'''
    # OS X Yosemite return 10.10, so we will be happy with len(...) == 2, then add 0 for last number
    try:
        mac_ver = tuple(int(n) for n in platform.mac_ver()[0].split('.'))
        assert 2 <= len(mac_ver) <= 3
    # pylint: disable=broad-except
    except Exception:
        return None
    if len(mac_ver) == 2:
        mac_ver = mac_ver + (0, )
    return mac_ver


def read_plist(plist_path):
    '''returns a plist object read from a file path'''
    # get a tempfile path for exporting our defaults data
    export_fifo = tempfile.mktemp()
    # make a fifo for defaults export in a temp file
    os.mkfifo(export_fifo)
    # export to the fifo
    osx_version = get_macos_version()
    if osx_version[1] >= 9:
        subprocess.Popen(
            ['/usr/bin/defaults', 'export', plist_path, export_fifo]).communicate()
        # convert the export to xml
        plist_string = subprocess.Popen(
            ['/usr/bin/plutil', '-convert', 'xml1', export_fifo, '-o', '-'],
            stdout=subprocess.PIPE).stdout.read()
    else:
        try:
            cmd = ['/usr/libexec/PlistBuddy', '-x', '-c', 'print', plist_path]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            plist_string = proc.communicate()[0]
        # pylint: disable=broad-except
        except Exception:
            return None
    # parse the xml into a dictionary
    user_plist = plistlib.loads(plist_string)
    return user_plist


def get_running_processes():
    '''Returns a list of paths of running processes'''
    proc = subprocess.Popen(['/bin/ps', '-axo' 'comm='],
                            shell=False, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    (output, dummy_err) = proc.communicate()
    if proc.returncode == 0:
        proc_list = [item for item in output.splitlines()
                     if item.startswith(b'/')]
        launchcfmapp = ('/System/Library/Frameworks/Carbon.framework'
                        '/Versions/A/Support/LaunchCFMApp')
        if launchcfmapp in proc_list:
            # we have a really old Carbon app
            proc = subprocess.Popen(['/bin/ps', '-axwwwo' 'args='],
                                    shell=False, stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            (output, dummy_err) = proc.communicate()
            if proc.returncode == 0:
                carbon_apps = [item[len(launchcfmapp)+1:]
                               for item in output.splitlines()
                               if item.startswith(launchcfmapp)]
                if carbon_apps:
                    proc_list.extend(carbon_apps)
        return proc_list
    else:
        return []


def is_app_running(appname):
    '''Tries to determine if the application in appname is currently
    running'''
    proc_list = get_running_processes()
    matching_items = []
    if appname.startswith('/'):
        # search by exact path
        matching_items = [item for item in proc_list
                          if item == appname]
    elif appname.endswith('.app'):
        # search by filename
        matching_items = [item for item in proc_list
                          if '/'+ appname + '/Contents/MacOS/' in item]
    else:
        # check executable name
        matching_items = [item for item in proc_list
                          if item.endswith(bytes('/' + appname, 'utf-8'))]
    if not matching_items:
        # try adding '.app' to the name and check again
        matching_items = [item for item in proc_list
                          if bytes('/'+ appname + '.app/Contents/MacOS/', 'utf-8') in item]

    if matching_items:
        # it's running!
        return True

    # if we get here, we have no evidence that appname is running
    return False


def launch_depnotify():
    '''Launch DEPNotify'''
    dn_path = '/Applications/Utilities/DEPNotify.app'
    subprocess.call(['/usr/bin/open', dn_path, '--args', '-munki'])


def kill_depnotify():
    '''Kill DEPNotify process'''
    subprocess.call(['/usr/bin/killall', 'DEPNotify'])


def main():
    '''Main thread'''
    plist_path = os.path.expanduser(
        '~/Library/Preferences/com.apple.dock.plist')
    # Wait for mod-count to be > 1 because dock is still being setup by Apple.
    # Apps shouldn't try and launch before this.
    if os.stat(plist_path).st_uid == os.stat('/dev/console').st_uid:
        plist_to_read = read_plist(plist_path)
        mod_count = int(plist_to_read.get('mod-count', 0))
        seconds_waited = 0
        while mod_count < 2 and seconds_waited < 5:
            print('Waiting for initial dock setup. mod-count is: %s' % mod_count)
            time.sleep(1)
            seconds_waited += 1
            print('Waited %s seconds so far' % seconds_waited)
            plist_to_read = read_plist(plist_path)
            mod_count = int(plist_to_read.get('mod-count', 0))
        if mod_count < 2:
            print('Timed out waiting for dock to be setup.')

    if is_app_running('DEPNotify'):
        # If a "quit" command has previously been sent to DEPNotify, it will not
        # update its status even if the log file is purged. Because of this, we force
        # to relaunch DEPNotify so it will refresh.
        print('DEPNotify running - relaunching!')
        kill_depnotify()
        time.sleep(0.5)
        launch_depnotify()
    else:
        print('Launching DEPNotify!')
        launch_depnotify()


if __name__ == '__main__':
    main()
