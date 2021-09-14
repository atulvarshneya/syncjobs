#!/usr/bin/python3

import os
import signal
import time
import sys
import config

# Read the registry and setup jobs file, pid dir, and log file
reg = config.Config("/home/pi/syncjobs/etc/registry").read_registry()
RUNDIR = reg["rundir"]

def findactive(RUNDIR):
	activepid = None
	with os.scandir(RUNDIR) as scnitr:
		for p in scnitr:
			if os.path.exists("/proc/"+p.name):
				activepid = int(p.name)
	return activepid


def rem_inactivepids(RUNDIR):
	inactivepid = []
	with os.scandir(RUNDIR) as scnitr:
		for p in scnitr:
			if not os.path.exists("/proc/"+p.name):
				print("Removing leftover pid file", p.name)
				os.remove(RUNDIR+"/"+p.name)

sjpid = findactive(RUNDIR)
if not sjpid is None:
	os.kill(sjpid, signal.SIGTERM)
	print("Sent TERMINATE signal to {:d}. Waiting for its exit.".format(sjpid))
	for i in range(5):
		if not os.path.exists("/proc/"+str(sjpid)):
			print("syncjobs exited.")
			break
		else:
			print("waiting ...")
			time.sleep(2)

	if os.path.exists("/proc/"+str(sjpid)):
		print("syncjobs did not exit.")

rem_inactivepids(RUNDIR)

sys.exit(0)
