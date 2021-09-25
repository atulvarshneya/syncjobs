#!/usr/bin/python3

import os
import sys
import syncjobs.config as config
import datetime
import argparse
import syncjobs.pushnoti as pushnoti
import syncjobs.logger as logger
import syncjobs.coreops as core

#####################################################################
## MAIN
#####################################################################

### Read the registry and setup jobs file, pid dir, and log file
regfile = os.environ.get("SJREGISTRY")
if regfile is None:
	regfile = "~/.sjregistry"
reg = config.Config(regfile).read_registry()
LOGFILE = reg["logfile"]
if LOGFILE == "":
	LOGFILE = "/home/pi/syncjobs/log/syncjobs.log"
JOBSFILE = reg["jobsloc"]
RUNDIR = reg["rundir"]
MAXLOGSZ = int(reg["maxlogsz"])
logger.loglevel = int(reg["loglevel"])
webui_url = reg["webui"]

### Roll over the logfile if larger than MAXLOGSZ
if os.path.exists(LOGFILE) and os.stat(LOGFILE).st_size > MAXLOGSZ:
	d = datetime.datetime.now()
	fnameold = LOGFILE+"."+d.strftime("%Y%m%d")
	os.replace(LOGFILE,fnameold)

### Commandline arguments, do it after reading registry to enable overriding
parser = argparse.ArgumentParser(description="My own synctoy replacement")
parser.add_argument("-i", action="store_true", help="Show all logging on screen")
parser.add_argument("-l", default=logger.loglevel, type=int, help="Logging level")
args = parser.parse_args()
logger.loglevel = args.l
if not args.i:
	logfile = open(LOGFILE,"a")
	sys.stdout = logfile
	sys.stderr = logfile
else:
	print("Logging on screen")

### CHECK if an instance is already running
with os.scandir(RUNDIR) as scnitr:
	for p in scnitr:
		if os.path.exists("/proc/"+p.name):
			logger.log(0,"....................................................................")
			logger.log(0,"BACKING OFF NEW RUN. An instance already running. Pid =",p.name)
			logger.log(0,"....................................................................")
			sys.exit(2)
		else:
			logger.log(2,"Removing leftover pid file", p.name)
			os.remove(RUNDIR+"/"+p.name)
selfpid = os.getpid()
selfname = "{:s}/{:d}".format(RUNDIR,selfpid)
open(selfname,"a").close()

### START
logger.log(0,"STARTED ============================================================")

totnumerrs, totmkdir, totcpfile, totdldir, totdlfile = (0,0,0,0,0)
## go over each job
logger.log(2,"JOBSFILE =", JOBSFILE)
jobs = config.Config(JOBSFILE).read_entries()
for j in jobs:

	SRCDIR = j[1]
	DSTDIR = j[2]
	syncflags = j[3]

	logger.log(1,"Processing job: {:s}, source: {:s}, destination: {:s}, syncflags: {:s}".format(j[0], SRCDIR, DSTDIR, syncflags))

	fullist = {}
	updlist = {}
	dellist = {}
	core.listdir(SRCDIR,fullist)
	logger.log(2,"Completed scanning", SRCDIR)
	core.checkdir(DSTDIR,fullist,updlist,dellist)
	logger.log(2,"Completed comparing with", DSTDIR)

	logger.log(2, "Applying deltas ...")
	(mkdir, cpfile, dldir, dlfile, numerr) = \
		core.apply_newupddel(SRCDIR,DSTDIR, fullist, updlist, dellist, syncflags)
	totmkdir = totmkdir + mkdir
	totcpfile = totcpfile + cpfile
	totdldir = totdldir + dldir
	totdlfile = totdlfile + dlfile
	totnumerrs = totnumerrs + numerr
	logger.log(1,"Completed job: {:s}".format(j[0]))
	logger.log(1,"")

msg = "Created dirs:  {:5d}\nCopied files:  {:5d}\nDeleted dirs:  {:5d}\nDeleted files: {:5d}\nERRORS  {:5d}\n".format(totmkdir,totcpfile,totdldir,totdlfile,totnumerrs)
pushnoti.pushnotify("syncjobs completed.\n" + msg, webui_url=webui_url)

os.remove(selfname)

### COMPLETION
logger.log(0,"COMPLETED ==========================================================")
logger.log(0,"")
