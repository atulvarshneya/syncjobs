#!/bin/bash

logfile=$(grep "^logfile" /shares/USBDRIVE/SYNCJOBS.conf/etc/registry | cut -d: -f2)
echo $logfile

tail -n100 -f $logfile
