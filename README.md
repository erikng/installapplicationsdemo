# InstallApplications Demo
This repository is a full example of how to use [InstallApplications](https://github.com/erikng/installapplications) in a production environment.

It has been updated for the new Python 3.9 embedded version of InstallApplications. This version should support M1 macs

Some interesting things to look at:
- a fork of [dockutil](https://github.com/kcrawford/dockutil) for use exclusively with the embedded Python
- a script to bless VM's for use with FileVault encryption
- a script to silently caffeinate a machine and continue on with provisioning
- a script to customize DEPNotify, as well as examples in other scripts to further give information to the user
- a script to bootstrap Munki with a specific "DEP" provisioning manifest
- a script to silently run Munki in "auto" mode after provisioning is complete
- a script to enable Munki's LaunchDaemons without requiring a reboot, utilizing official Munki packages
- a script to show a basic example of how the preflight works, enabling you to only run InstallApplications when needed
- a user script to intelligently launch DEPNotify
- a user script to intelligently configure a dock
