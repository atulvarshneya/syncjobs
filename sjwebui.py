#!/usr/bin/python3

import os
import config
from flask import Flask
from flask import render_template

app = Flask(__name__)

def readreg():
	regfile = os.environ.get("SJREGISTRY")
	if regfile is None:
		regfile = "~/.sjregistry"
	reg = config.Config(regfile).read_registry()
	return reg

@app.route('/')
def regfile():
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
fmlast = 0
scrframe = 0
total_credirs, total_cpfiles, total_deldirs, total_delfiles, total_errors = 0,0,0,0,0

@app.route('/logfile')
def logfile():
	global frames, fmtots, fmlast, scrframe
	global total_credirs, total_cpfiles, total_deldirs, total_delfiles, total_errors

	reg = readreg()
	frames = []
	fmtots = []
	fmlast = 0
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
				fmtots.append((total_credirs, total_cpfiles, total_deldirs, total_delfiles, total_errors))
				fmlast = fmlast + 1
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
		fmtots.append((total_credirs, total_cpfiles, total_deldirs, total_delfiles, total_errors))
		scrframe = fmlast
	return render_template('logs.html', frames=frames, scrframe=scrframe, fmtots=fmtots, fmlast=fmlast)

@app.route('/frame/<frameidstr>')
def frame(frameidstr):
	global scrframe

	scrframe = int(frameidstr)
	if scrframe < 0 or scrframe > fmlast:
		logfile()
	return render_template('logs.html', frames=frames, scrframe=scrframe, fmtots=fmtots, fmlast=fmlast)


if __name__ == '__main__':
	app.run(host="0.0.0.0", port=5000, debug=False)
