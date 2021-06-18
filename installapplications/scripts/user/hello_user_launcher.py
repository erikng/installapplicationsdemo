#!/Library/installapplications/Python.framework/Versions/Current/bin/python3
'''hello launcher'''
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


def launch_hello():
    '''Launch hello'''
    dn_path = '/Applications/Utilities/hello.app'
    subprocess.call(['/usr/bin/open', dn_path, '--args', '-json-url', 'https://raw.githubusercontent.com/erikng/installapplicationsdemo/main/hello/com.github.erikng.hello.json'])


def kill_hello():
    '''Kill hello process'''
    subprocess.call(['/usr/bin/killall', 'hello'])


def main():
    '''Launch hello'''
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
        print('Delaying hello launch by 5 seconds due to Big Sur flakiness')
        time.sleep(5)

    if is_app_running('hello'):
        print('hello running - relaunching!')
        kill_hello()
        time.sleep(0.5)
        launch_hello()
    else:
        print('Launching hello!')
        launch_hello()


if __name__ == '__main__':
    main()
