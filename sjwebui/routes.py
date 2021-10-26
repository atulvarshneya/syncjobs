#!/usr/bin/python3

import os
import syncjobs.config as config
from flask import render_template, flash, redirect, url_for
from sjwebui import app

def readreg():
	regfile = os.environ.get("SJREGISTRY")
	if regfile is None:
		regfile = "~/.sjregistry"
	reg = config.Config(regfile).read_registry()
	return reg

@app.route('/')
def home():
	reg = readreg()
	return render_template('home.html', reg=reg)

@app.route('/jobfile')
def jobfile():
	reg = readreg()
	jobfile = reg["jobsloc"]
	jobs = config.Config(jobfile).read_entries()
	return render_template('jobs.html', jobs=jobs)

frames = []
fmtots = []
fmtmstamp = []
fmlast = 0
scrframe = 0

@app.route('/logfile')
def logfile():
	global frames, fmtots, fmlast, scrframe, fmtmstamp

	reg = readreg()
	frames = []
	fmtots = []
	fmtmstamp = []
	fmlast = 0
	scrframe = 0
	logtext = "-no entry-"
	tmstamp = "-no entry-"
	total_credirs, total_cpfiles, total_deldirs, total_delfiles, total_errors = 0,0,0,0,0
	with open(reg["logfile"], "r") as lfd:
		while True:
			ln = lfd.readline()
			if not ln:
				break
			if ln[20:27] == "STARTED":
				frames.append(logtext)
				fmtots.append((total_credirs, total_cpfiles, total_deldirs, total_delfiles, total_errors))
				fmtmstamp.append(tmstamp)
				fmlast = fmlast + 1
				logtext = ""
				tmstamp = ln[0:19]
				total_credirs, total_cpfiles, total_deldirs, total_delfiles, total_errors = 0,0,0,0,0
			if ln[20:32] == "Created dirs":
				total_credirs = total_credirs + int(ln[33:])
			if ln[20:33] == "Copied  files":
				total_cpfiles = total_cpfiles + int(ln[34:])
			if ln[20:32] == "Deleted dirs":
				total_deldirs = total_deldirs + int(ln[33:])
			if ln[20:33] == "Deleted files":
				total_delfiles = total_delfiles + int(ln[34:])
			if ln[20:26] == "ERRORS":
				total_errors = total_errors + int(ln[27:])
			logtext = logtext + ln
		frames.append(logtext)
		fmtots.append((total_credirs, total_cpfiles, total_deldirs, total_delfiles, total_errors))
		fmtmstamp.append(tmstamp)
		scrframe = fmlast
	return render_template('logs.html', frames=frames, scrframe=scrframe, fmtmstamp=fmtmstamp, fmtots=fmtots, fmlast=fmlast)

@app.route('/frame/<frameidstr>')
def frame(frameidstr):
	global scrframe, frames, fmtots, fmtmstamp, fmlast

	scrframe = int(frameidstr)
	if scrframe < 0 or scrframe >= fmlast:
		return redirect(url_for('logfile'))
	return render_template('logs.html', frames=frames, scrframe=scrframe, fmtmstamp=fmtmstamp, fmtots=fmtots, fmlast=fmlast)
