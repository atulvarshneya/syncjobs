Using syncjobs.py

0. To be able to mount the USBDRIVE (as SJData) on Windows PCs, install and setup OpenMediaVault (OMV) first on the Raspberry Pi
   Next,
       sudo mkdir /shares
	   sudo ln -s <the mount point of OMV> /shares/USBDRIVE

1. Files
Registry file -
	* default location is ~/.sjregistry. Can override by environment variable SJREGISTRY
		- Current setup (in ~/.bashrc) - export SJREGISTRY=/shares/USBDRIVE/SYNCJOBS.conf/etc/registry
	* contains 
		- location of file listing the jobs
		jobsloc:/shares/USBDRIVE/SYNCJOBS.conf/etc/jobs

		- location of log file
		logfile:/shares/USBDRIVE/SYNCJOBS.conf/log/syncjobs.log

		- location of run dir
		rundir:/shares/USBDRIVE/SYNCJOBS.conf/run

		- maximum logfile size
		maxlogsz:250000

		- logging details level
		loglevel:4

		- Push otification information (using Pushover service)
		pushnotify:off
		app-token:aumj5i8rc3mt6qb6mu52x2r946ozf7
		user-key:uxntk5wn9hqxinkcs7w2i6pdbqtjb3

		- Email notification information
		emaiilnotify:on
		smtp-server:smtp.gmail.com
		smtp-port:587
		gmail-username:home.varshneya@gmail.com
		gmail-password:xxxx
		recipient:atul.varshneya@gmail.com

		- SJ WebGUI URL; can put the logfile display URL
		webui:http://netdisk1.lan:5000/logfile

Jobs file -
	* lists the sync jobs. Format is as
		# <job name>:<source folder location>:<dst folder location>:<sync or contribute>:<maxdeletes><optioanlly :mountchk>
	For example
		Common:/media/Common:/shares/USBDRIVE/SYNCJOBS/Common:sync:50:mountchk
		Library:/media/Library:/shares/USBDRIVE/SYNCJOBS/Library:sync:200
	if maxdeletes id exceeded the deltas are not applied, irrespective of <sync or contribute> flag; since something is too off

Log file
	* This file can grow up to the size specified in registry, and then is moved to <logfilename>.<yyyymmdd>
	* The level of details logged at different logging levels are given in loglevels.txt
	* The log level is selected in registry, can be overriden from commandline
		$ ./syncjobs.py -l4

run dir
	* this dir is used to store the pid of the currently running syncjobs.py
	* if a process with that pid is running, a new syncjobs.py will exit to let the running instance do its job

2. Setting up syncjobs

mount the data drive
	* mount at, say, /shares/USBDRIVE the drive to use as the destination for sync'ing the data
	* add a line in /ets/fstab for auto mounting of the drive (if using userid pi, else replace with the correct one)
		UUID=F0806AB5806A81C8 /shares/USBDRIVE ntfs uid=pi,gid=pi 0 0

mount all source drives (likely network drives)
	* mount the sources at, say, /media/drive1, ...
	* add lines in /etc/fstab for auto mounting the source [network] drives (if using userid pi, else replace with the correct one)
		//netdisk2.lan/Common /media/Common cifs username=guest,password=,uid=pi,gid=pi 0 0

create a jobs file
	* format of jobs file is given above

setup registry file
	* format of registry file is given above

crontab entry
	* use crontab -e to create crontab entry to periodically run syncjobs.py  (if using userid pi, else replace with the correct one)
		SJREGISTRY=/shares/USBDRIVE/SYNCJOBS.conf/etc/registry
		0 */3 * * * /home/pi/syncjobs/syncjobs.py -l4

3. setting up sjwebui (Web UI for SyncJobs)

Follow steps in Webui-service.txt
