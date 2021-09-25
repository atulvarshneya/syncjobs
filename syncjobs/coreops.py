#!/usr/bin/python3

import os
import sys
import shutil as su
import datetime
import time
import syncjobs.logger as logger


def listdir(path,contents_list):
	# we want to work independently of the location where the volume is mounted
	# so chdir'ing to the root location so "." becomes the starting point
	origdir = os.getcwd()
	os.chdir(path)
	try:
		dirlist = ["."]
		while (len(dirlist) > 0):
			d = dirlist.pop(0)
			st = os.stat(d)
			with os.scandir(d) as scnitr:
				for f in scnitr:
					fname = f.name if d == "." else d+"/"+f.name
					st = os.stat(fname)
					if (st.st_mode & 0o140000 != 0):
						if (st.st_mode & 0o040000) == 0o040000:
							dirlist.append(fname)
						contents_list[fname] = (st.st_mode, st.st_size, round(st.st_mtime,4))
					else:
						logger.log(2,"Ignoring {:s}, not a file or a directory. st_mode = {:06o}".format(fname,st.st_mode))
	finally:
		os.chdir(origdir)

def checkdir(dstpath, fullist, updlist, dellist):
	origdir = os.getcwd()
	os.chdir(dstpath)
	try:
		dirlist = ["."]
		while (len(dirlist) > 0):
			d = dirlist.pop(0)
			with os.scandir(d) as scnitr:
				for f in scnitr:
					fname = f.name if d == "." else d+"/"+f.name
					st = os.stat(fname)
					if (st.st_mode & 0o040000) == 0o040000:
						dirlist.append(fname)
					fmd,fsz,ftm = st.st_mode, st.st_size, round(st.st_mtime,4)
					if fname in fullist:
						md,sz,tm = fullist[fname]
						if (fmd & 0o140000 == 0o040000) and (md & 0o140000 == 0o040000):
							logger.log(6,"DIR UPTODATE", fname, ftm, tm)
							fullist.pop(fname)
						elif (fmd & 0o140000 == 0o040000) and (md & 0o140000 == 0o100000):
							logger.log(5,"ADDING dir to dellist","'"+fname+"'", "not present in source")
							dellist[fname] = (fmd, fsz, ftm)
							# and DO NOT POP from fullist.
						elif (fmd & 0o140000 == 0o100000) and (md & 0o140000 == 0o100000):
							if (fsz != sz) or (ftm < tm):
								logger.log(5,"ADDING file to updlist","'"+fname+"'")
								updlist[fname] = (md, sz, tm)
							else:
								logger.log(6,"FILE UPTODATE", fname, ftm, tm)
							fullist.pop(fname)
						elif (fmd & 0o140000 == 0o100000) and (md & 0o140000 == 0o040000):
							logger.log(5,"ADDING file to dellist","'"+fname+"'", "not present in source")
							dellist[fname] = (fmd, fsz, ftm)
							# and DO NOT POP from fullist.
						else:
							logger.log(2,"Ignoring '{:s}', not a file nor a directory. st_mode = {:06o}".format(fname,fmd))
							fullist.pop(fname)
					else:
						logger.log(5,"ADDING item to dellist","'"+fname+"'", "not present in source")
						dellist[fname] = (fmd, fsz, ftm)
	finally:
		os.chdir(origdir)

def apply_newupddel(src, dst, newlist, updlist, dellist, syncflags):
	errorlist = {}
	num_makedir = 0
	num_copyfile = 0
	num_delfile = 0
	num_deldir = 0
	num_errors = 0

	## deletes first, make space before using it, and enable overwrites on dir -> file, file -> dir
	if syncflags == "sync":
		# deletions pass 1: first delete the files
		for f in dellist.keys():
			try:
				md,sz,tm = dellist[f]
				fname = dst+"/"+f
				if md & 0o100000:
					logger.log(4,"DELETE FILE: ({:,d}) {:s}".format(sz,f))
					os.remove(fname)
					num_delfile = num_delfile + 1
			except:
				logger.log(2,"FILE DEL ERROR",f)
				errorlist[f] = dellist[f]
				num_errors = num_errors + 1
		logger.log(2, "Files (deleted) removing done")

		# deletions pass 2: now delete the directories
		for f in dellist.keys():
			try:
				md,sz,tm = dellist[f]
				dirname = dst+"/"+f
				if md & 0o040000:
					logger.log(4,"DELETE DIR:", f)
					os.rmdir(dirname)
					num_deldir = num_deldir + 1
			except:
				logger.log(2,"DIR DEL ERROR",f)
				errorlist[f] = dellist[f]
				num_errors = num_errors + 1
		logger.log(2, "Directories (deleted) removing done")
	### endif syncflags == "sync"

	## Compute total data size and number of files to copy
	totalsz = 0
	num_totalfiles = 0
	for li in [updlist, newlist]:
		for f in li.keys():
			md,sz,tm = li[f]
			totalsz = totalsz + sz
			if md & 0o100000 == 0o100000:
				num_totalfiles = num_totalfiles + 1
	copiedsz = 0

	# pass 1: make dir tree first
	for fileslist in [updlist, newlist]:
		for f in fileslist.keys():
			try:
				md,sz,tm = fileslist[f]
				dirname = dst+"/"+f
				if md & 0o040000:
					logger.log(4,"MAKE DIR:",f)
					os.makedirs(dirname, exist_ok=True)
					num_makedir = num_makedir + 1
			except:
				logger.log(2,"DIR MAKE ERROR", f)
				errorlist[f] = fileslist[f]
				num_errors = num_errors + 1
	logger.log(2, "Directories creating done")

	# pass 2: now populate the files
	tmstamp1 = time.time()
	for fileslist in [updlist,newlist]:
		for f in fileslist.keys():
			try:
				md,sz,tm = fileslist[f]
				srcfname = src+"/"+f
				dstfname = dst+"/"+f
				if md & 0o100000:
					logger.log(4,"COPY FILE: ({:,d}) {:s}".format(sz, f))
					su.copy2(srcfname, dstfname, follow_symlinks=False)
					num_copyfile = num_copyfile + 1
					copiedsz = copiedsz + sz
					tmstamp2 = time.time()
					cprate = copiedsz / (tmstamp2 - tmstamp1)
					pctdone = int(100 * copiedsz / totalsz)
					remtm = int((totalsz - copiedsz)/cprate)
					remhr, remmin, remsec = int(remtm/3600), int((remtm % 3600)/60), remtm % 60

					logger.log(3, "Completed {:,d} / {:,d} [{:,d} / {:,d} {:d}% @ {:.2f}Mb/s]. Estimated remaining time: {:d}:{:02d}:{:02d}".format(
						num_copyfile, num_totalfiles, 
						copiedsz, totalsz, pctdone, cprate/1048567.0,
						remhr,remmin,remsec))
			except:
				logger.log(2,"FILE COPY ERROR", f)
				errorlist[f] = fileslist[f]
				num_errors = num_errors + 1
	logger.log(2, "Files (new, updated) copying done")

	logger.log(1,"Created dirs\t", num_makedir)
	logger.log(1,"Copied  files\t", num_copyfile)
	logger.log(1,"Deleted dirs\t", num_deldir)
	logger.log(1,"Deleted files\t", num_delfile)
	logger.log(1,"ERRORS       \t", num_errors)

	return (num_makedir, num_copyfile, num_deldir, num_delfile, num_errors)

##Non-essential functions - can delete them later on#################
#####################################################################

def save_list(file, contents_list):
	fd = open(file,"w")
	for k in contents_list.keys():
		md,sz,tm = contents_list[k]
		fd.write("{:d}|{:d}|{:.4f}|{:s}\n".format(md,sz,tm,k))
	fd.close()

def read_list(file, contents_list):
	fd = open(file,"r")
	while True:
		line = fd.readline()
		line = line.rstrip("\n")
		if not line:
			break
		md,sz,tm,f = line.split("|")
		contents_list[f] = (int(md),int(sz),float(tm))
	fd.close()
#####################################################################

