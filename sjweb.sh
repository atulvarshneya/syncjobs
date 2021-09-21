#!/usr/bin/bash

export SJREGISTRY=/shares/USBDRIVE/SYNCJOBS.conf/etc/registry
/home/pi/syncjobs/webui.py 2>&1 >> /shares/USBDRIVE/SYNCJOBS.conf/log/webui.log
