#!/usr/bin/bash

export SJREGISTRY=/shares/USBDRIVE/SYNCJOBS.conf/etc/registry

logfile=$(grep '^logfile' $SJREGISTRY | cut --delimiter=':' -f2)
echo "STARTING =================="
/home/pi/syncjobs/sjwebui.py
