#!/usr/bin/python3

import sys
import datetime

loglevel = 4

def log(importance, *args, **kwargs):
	global loglevel
	if importance <= loglevel:
		d = datetime.datetime.now()
		print(d.strftime("%Y/%m/%d %T"), end=" ")
		print(*args, **kwargs)
		sys.stdout.flush()
		sys.stderr.flush()

