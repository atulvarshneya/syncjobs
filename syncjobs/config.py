#!/usr/bin/python3

import os

class Config:
	def __init__(self,cfile,sep=':'):
		self.file = cfile
		self.entries = []
		self.registry = {}
		self.sep = sep

	def read_entries(self):
		with open(self.file,"r") as fd:
			while True:
				ln = fd.readline()
				if not ln:
					break
				ln = ln.strip()
				if len(ln) != 0 and ln[0] != '#':
					tokens = ln.split(self.sep)
					self.entries.append(tokens)
		return self.entries

	def get_entries(self):
		return self.entries

	def read_registry(self):
		with open(self.file,"r") as fd:
			while True:
				ln = fd.readline()
				if not ln:
					break
				ln = ln.strip()
				if len(ln) != 0 and ln[0] != '#':
					tokens = ln.split(self.sep,1)
					self.registry[tokens[0]] = tokens[1]
		return self.registry

	def get_registry(self):
		return self.registry

	def lookup_registry(self,key):
		return self.registry[key]

if __name__ == "__main__":
	regfile = os.environ.get("SJREGISTRY")
	if regfile is None:
		regfile = "~/.sjregistry"
	regobj = Config(regfile)
	reg = regobj.read_registry()
	for i,v in reg.items():
		print(i,v)

	jobsobj = Config(reg["jobsloc"])
	jobs = jobsobj.read_entries()
	for i in jobs:
		print(i[0],":")
		for idx in range(1,len(i)):
			print("\t", i[idx])
