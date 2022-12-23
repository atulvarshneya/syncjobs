#!/usr/bin/python3

import os
import sys
import syncjobs.config as config
import datetime
import argparse
import syncjobs.pushnotify as pushnoti
import syncjobs.emailnotify as emailnoti
import syncjobs.logger as logger
import syncjobs.coreops as core
import syncjobs.getmounts as getmounts

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
PUSHNOTI=reg["pushnotify"]
EMAILNOTI=reg["emailnotify"]
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
parser.add_argument("-j", type=str, default="", help="Job name")
parser.add_argument("-c", action="store_true", help="List the registry and jobs details, and exit")
args = parser.parse_args()
if args.c:
	for r,regval in reg.items():
		if r[0] == '-':
			regval = '<hidden>'
		print(f'REG {r:15s} {regval}')
	jobs = config.Config(JOBSFILE).read_entries()
	lth = [0,0,0,0,0,0]
	for j in jobs:
		for fid in range(6):
			lth[fid] = max(lth[fid], len(j[fid]))
	fmt = 'JOB {0:'+f'{lth[0]}'+'} '+'{1:'+f'{lth[1]}'+'} '+'{2:'+f'{lth[2]}'+'} '+'{3:'+f'{lth[3]}'+'} '+'{4:>'+f'{lth[4]}'+'} '+'{5:'+f'{lth[5]}'+'}'
	for j in jobs:
		print(fmt.format(j[0], j[1], j[2], j[3], j[4], j[5]))
	exit(0)

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

## get a map of all mounted filesystems
allmnts = getmounts.getmounts()

totnumerrs, totmkdir, totcpfile, totdldir, totdlfile = (0,0,0,0,0)
## go over each job
logger.log(2,"JOBSFILE =", JOBSFILE)
jobs = config.Config(JOBSFILE).read_entries()
for j in jobs:

	if args.j != '' and args.j != j[0]:
		continue
	SRCDIR = j[1]
	DSTDIR = j[2]
	syncflags = j[3]
	maxdels = 0 if not j[4].isdigit() else int(j[4])

	# check for optional mount flag
	mountflag = "<absent>"
	if len(j) > 5 and j[5] == "mountchk":
		mountflag = j[5]
		# check if SRCDIR is a mountpoint for a current fs mount
		if SRCDIR in allmnts.keys():
			mntsrc = allmnts[SRCDIR]
			mountOK = True
		else:
			mountOK = False

	logger.log(1,"Processing job: {:s}, source: {:s}, destination: {:s}, syncflags: {:s}, mountflag: {:s}".format(j[0], SRCDIR, DSTDIR, syncflags, mountflag))
	if mountflag == "mountchk" and not mountOK:
		logger.log(1,"MOUNT CHECK FAILED. Skipping job.")
		(mkdir, cpfile, dldir, dlfile, numerr) = (0, 0, 0, 0, 1)
	else:
		fullist = {}
		updlist = {}
		dellist = {}
		core.listdir(SRCDIR,fullist)
		logger.log(2,f"Completed scanning {SRCDIR}, [{len(fullist)} files]")
		core.checkdir(DSTDIR,fullist,updlist,dellist)
		logger.log(2,f"Completed comparing with {DSTDIR}, [{len(updlist)} upds, {len(dellist)} dels]")
		if len(dellist) > maxdels:
			logger.log(2,"Files to delete = {:d} exceeds max configured for this job = {:d}".format(len(dellist),maxdels))
			logger.log(2, "SKIPPING DELTAS ...")
			(mkdir, cpfile, dldir, dlfile, numerr) = (0, 0, 0, 0, 1)
			logger.log(1,"DELTA ERRORS \t", 1)
		else:
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

msg = "syncjobs completed.\nCreated dirs:  {:5d}\nCopied files:  {:5d}\nDeleted dirs:  {:5d}\nDeleted files: {:5d}\nERRORS  {:5d}\n".format(totmkdir,totcpfile,totdldir,totdlfile,totnumerrs)
if PUSHNOTI == "on":
	pushnoti.pushnotify(msg, webui_url=webui_url)
if EMAILNOTI == "on":
	emailnoti.emailnotify(msg, webui_url=webui_url)

os.remove(selfname)

### COMPLETION
logger.log(0,"COMPLETED ==========================================================")
logger.log(0,"")
