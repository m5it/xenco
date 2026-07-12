"""
---------------------------
--== xMagic ==-- by madK0s
---------------------------

generate magic file for xEnco

example run:

#-- retrive random chars
python xMagic.py -s

#-- set seed on which later is generated text
python xMagic.py -s -S 30

#-- Use all readable ascii chars. ( default )
python xMagic.py -s -S 30 -f 32 -t 127

#-- Use all 255 char bytes
python xMagic.py -s -S 30 -f 0 -t 255
"""

import random
import sys,getopt

cntFrom  = 32
cntTo    = 128
seed     = None
seedSalt = 759124791239348
silent   = True

#--
def get(Seed=None, From=None, To=None):
	global cntFrom,cntTo,seed,silent,seedSalt
	
	if From is not None:
		cntFrom = From
	if To is not None:
		cntTo   = To
	if Seed is not None:
		seed = Seed
	
	a       = []
	content = ""
	
	for i in range(cntFrom,cntTo):
		a.append(chr(i))
	
	tmpseed = seed
	if tmpseed is not None:
		tmpseed+seedSalt
	
	random.seed(tmpseed)
	random.shuffle(a)
	
	for i in range(len(a)):
		content += a[i]
	
	if not silent:
		print(content)
	return content

#--
def main(argv):
	global seed,cntFrom,cntTo,silent
	
	try:
		opts, args = getopt.getopt(argv,"shS:f:t:",[])
	except getopt.GetoptError:
		print('need help... :) d1"')
		sys.exit(2)
	#--
	for opt, arg in opts:
		if opt=="-h":
			print("need help... :) d2")
			sys.exit(2)
		elif opt=="-S":
			seed = int(arg)
		elif opt=="-s":
			silent = False
		elif opt=="-f":
			cntFrom = int(arg)
		elif opt=="-t":
			cntTo = int(arg)
	
	get()

#--
if __name__ == '__main__':
	#--
	main(sys.argv[1:])
