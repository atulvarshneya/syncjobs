#!/usr/bin/python3

def getmounts():
	allmounts = {}
	with open("/proc/mounts","r") as fd:
		while True:
			ln = fd.readline()
			if not ln:
				break
			ln = ln.strip()
			if len(ln) != 0 and ln[0] != '#':
				tokens = ln.split(" ")
				mntpt = tokens[1].replace("\\040"," ")
				mntsrc = tokens[0].replace("\\040"," ")
				allmounts[mntpt] = mntsrc
	return allmounts

if __name__ == "__main__":
	am = getmounts()
	for k in am.keys():
		print(k," mounted from ",am[k])

	print()
	checkfor = '/media/Users Files'
	print("Check for ",checkfor,"----------------")
	if checkfor in am.keys():
		print(checkfor," found mounted from ", am[checkfor])
