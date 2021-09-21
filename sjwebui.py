#!/usr/bin/python3

"""basic Flask app - demo of using a variable in a route"""

import os
import config
from flask import Flask
app = Flask(__name__)


def readreg():
	regfile = os.environ.get("SJREGISTRY")
	if regfile is None:
		regfile = "~/.sjregistry"
	reg = config.Config(regfile).read_registry()
	return reg

def pageheader():
	titletext = "<h1>SyncJobs</h1>"
	links = "<p>" + \
		"<a href='/'>Home</a> &emsp; " + \
		"<a href='/logfile'>Log File</a> &emsp; " + \
		"<a href='/jobfile'>Jobs List</a> " + \
		"</p>"
	ruler = "<hr>"
	return titletext + links + ruler

@app.route('/')
def hello():
	reg = readreg()
	outtext = ""
	for r in reg.keys():
		outtext = outtext + \
			"<div style=\"font-size:16px\">" + \
			"<pre>" + \
			r + ":\n\t" + \
			reg[r] + "\n\n" + "</pre>"
		outtext = outtext + "</div>"
	return pageheader() + outtext

@app.route('/jobfile')
def jobfile():
	reg = readreg()
	jobfile = reg["jobsloc"]
	jobs = config.Config(jobfile).read_entries()
	outtext = ""
	for i in jobs:
		outtext = outtext + \
			"<p>" +\
			"<pre>" + \
			"\nJOB:  " + i[0] + \
			"\n\tSource      :\t" + i[1] + \
			"\n\tDestination :\t" + i[2] + \
			"\n\tFlags       :\t" + i[3] + \
			"</pre>" + \
			"</p>"
	return pageheader() + outtext

frames = []
totcnt = []
frameid = 0
scrframe = 0
total_credirs, total_cpfiles, total_deldirs, total_delfiles, total_errors = 0,0,0,0,0

@app.route('/logfile')
def logfile():
	global frames, totcnt, frameid, scrframe
	global total_credirs, total_cpfiles, total_deldirs, total_delfiles, total_errors

	reg = readreg()
	frames = []
	totcnt = []
	frameid = 0
	scrframe = 0
	logtext = ""
	total_credirs, total_cpfiles, total_deldirs, total_delfiles, total_errors = 0,0,0,0,0
	with open(reg["logfile"], "r") as lfd:
		while True:
			ln = lfd.readline()
			if not ln:
				break
			if ln[20:27] == "STARTED":
				frames.append(logtext)
				totcnt.append((total_credirs, total_cpfiles, total_deldirs, total_delfiles, total_errors))
				frameid = frameid + 1
				logtext = ""
				total_credirs, total_cpfiles, total_deldirs, total_delfiles, total_errors = 0,0,0,0,0
			if ln[20:32] == "Created dirs":
				total_credirs = total_credirs + int(ln[33:])
			if ln[20:33] == "Copied  files":
				total_cpfiles = total_cpfiles + int(ln[34:])
				# print(ln[0:20], "copied files", int(ln[34:]), total_cpfiles)
			if ln[20:32] == "Deleted dirs":
				total_deldirs = total_deldirs + int(ln[33:])
			if ln[20:33] == "Deleted files":
				total_delfiles = total_delfiles + int(ln[34:])
			if ln[20:26] == "ERRORS":
				total_errors = total_errors + int(ln[27:])
			logtext = logtext + ln
		frames.append(logtext)
		totcnt.append((total_credirs, total_cpfiles, total_deldirs, total_delfiles, total_errors))
		scrframe = frameid
	return pageheader() + framebar() + "<pre>" + frames[scrframe] + "</pre>" + "<hr>" + framebar()

def framebar():
	global frames, totcnt, frameid, scrframe

	nextframe = "/frame/{:d}".format(scrframe+1)
	prevframe = "/frame/{:d}".format(scrframe-1)
	(credirs,cpfiles,deldirs,delfiles,errors) = totcnt[scrframe]
	fbartext = "<p>"
	if (scrframe > 0):
		fbartext = fbartext + "<a href=" + prevframe + ">prev</a>"
	else:
		fbartext = fbartext + "prev"
	fbartext = fbartext + " move to "
	if (scrframe < frameid):
		fbartext = fbartext + "<a href=" + nextframe + ">next</a>"
	else:
		fbartext = fbartext + "next"
	fbartext = fbartext + "&emsp;" + \
		"| &emsp; Copied: Dirs "+str(credirs)+", Files "+str(cpfiles)+ \
		". &emsp; Deleted: Dirs "+str(deldirs)+", Files "+str(delfiles)+ \
		". &emsp; ERRORS: "+str(errors)
	fbartext = fbartext + "</p>"
	return fbartext

@app.route('/frame/<frameidstr>')
def frame(frameidstr):
	global scrframe

	scrframe = int(frameidstr)
	if scrframe < 0 or scrframe >= len(frames):
		logfile()
	return pageheader() + framebar() + "<pre>" + frames[scrframe] + "</pre>" + "<hr>" + framebar()


if __name__ == '__main__':
	app.run(host="0.0.0.0", debug=False)
