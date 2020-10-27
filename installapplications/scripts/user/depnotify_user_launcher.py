#!/Library/installapplications/Python.framework/Versions/Current/bin/python3
'''dockutil wrapper'''
# Written by Erik Gomez
import os
import platform
import plistlib
import subprocess
import tempfile
import time


def get_macos_version():
    """returns a tuple with the (major,minor,revision) numbers"""
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


def read_plist(plist_path, macos_version):
    """returns a plist object read from a file path"""
    # get a tempfile path for exporting our defaults data
    export_fifo = tempfile.mktemp()
    # make a fifo for defaults export in a temp file
    os.mkfifo(export_fifo)
    # export to the fifo
    if macos_version[1] >= 9:
        subprocess.Popen(
            ['defaults', 'export', plist_path, export_fifo]).communicate()
        # convert the export to xml
        plist_string = subprocess.Popen(
            ['plutil', '-convert', 'xml1', export_fifo, '-o', '-'],
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
    """Returns a list of paths of running processes"""
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
    """Tries to determine if the application in appname is currently
    running"""
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
    dn_path = '/Library/Application Support/UberInternal/CPE/Utilities/DEPNotify.app'
    subprocess.call(['/usr/bin/open', dn_path, '--args', '-munki'])


def kill_depnotify():
    '''Kill DEPNotify process'''
    subprocess.call(['/usr/bin/killall', 'DEPNotify'])


def main():
    '''Launch DEPNotify if IAs didnt do it'''
    plist_path = os.path.expanduser(
        '~/Library/Preferences/com.apple.dock.plist')
    macos_version = get_macos_version()
    # If we are modifying the currently logged in user's dock, wait for
    # mod-count to be > 1 because dock is still being setup by Apple
    if os.stat(plist_path).st_uid == os.stat('/dev/console').st_uid:
        plist_to_read = read_plist(plist_path, macos_version)
        mod_count = int(plist_to_read.get('mod-count', 0))
        seconds_waited = 0
        while mod_count < 2 and seconds_waited < 120:
            print('Waiting for initial dock setup. mod-count is: %s' % mod_count)
            time.sleep(1)
            seconds_waited += 1
            print('Waited %s seconds so far' % seconds_waited)
            plist_to_read = read_plist(plist_path, macos_version)
            mod_count = int(plist_to_read.get('mod-count', 0))
        if mod_count < 2:
            print('Timed out waiting for dock to be setup.')

    # Cover both checks since we don't know what OS version will be returned
    if macos_version[0] >= 11 or macos_version[1] >= 16:
        print('Delaying DEPNotify Launch by 5 seconds due to Big Sur flakiness')
        time.sleep(5)

    if is_app_running('DEPNotify'):
        # Since we no longer use InstallApplications to launch DEPNotify, if
        # we are bootstrapping, it is more than likely due to a enrollment
        # failure. If a "quit" command is sent to DEPNotify, it will not update
        # its status even if the log file is purged. Because of this, we need
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
