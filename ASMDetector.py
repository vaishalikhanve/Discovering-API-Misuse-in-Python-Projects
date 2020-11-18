import argparse
import subprocess
import json
import os
from os import listdir
import sys

#Get all python files from given directory
def fileList(dirname):
	flist = listdir(dirname)
	flist = [fp for fp in flist if fp.find('.py')>0]
	flist = list(set([fp.split('.')[0].strip() for fp in flist]))
	return flist

#generates ASMs from Control flow Graphs
def generate_asm(dirname):
	flist = fileList(dirname)
	for fp in flist:
		#Subprocess executing pycfg file used to generating algorithm Control Flow Graphs
		subprocess.call(['python3','/home/vkhanve/pycfg-0.1/pycfg/pycfg.py',dirname+'/'+fp+'.py', '-c'])
		#Subprocess executing ASM generating algorithm implemented in Python
		subprocess.call(['python3','ASM.py',dirname+'/'+fp,dirname])
		os.remove(dirname+'/'+fp+'.txt')
	return

#Generate Frequent ASMs
def generate_patterns(dirname,dest,exeType):
	generate_asm(dirname)
	machines = []
	npdmachines = [] #nonparametric data machines
	flist = fileList(dirname)
	for fp in flist:
		with open(dirname+'/'+fp+'_asm.txt') as jfile: 
			data=json.load(jfile)
		machines.append(data[0])
		npdmachines.append(data[1])
		if exeType == 'NoMisuseDetection':
			os.remove(dirname+'/'+fp+'_asm.txt')

	with open(dirname+'/ASM_MACHINES.txt','w') as fr:
		json.dump(machines,fr)
	with open(dirname+'/ASM_WithNoArguments_MACHINES.txt','w') as fq:
		json.dump(npdmachines,fq)
	#Subprocess executing Pattern generating algorithm implemented in Python
	subprocess.call(['python3','pattern.py',dirname+'/ASM_MACHINES',dest+'/Arg','trainDataSet'])
	subprocess.call(['python3','pattern.py',dirname+'/ASM_WithNoArguments_MACHINES',dest+'/NoArg','trainDataSet'])
	os.remove(dirname+'/ASM_MACHINES.txt')
	os.remove(dirname+'/ASM_WithNoArguments_MACHINES.txt')
	return 

#Main funtion parsing command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('trainfile', help='Directory containing train dataset files' )
parser.add_argument('testfile', help='directory containing test dataset files or final result destination folder')
parser.add_argument('-p','--pattern', action='store_true', help='generate pattern from training file')
parser.add_argument('-mu','--misuseInUsage', action='store_true', help='detects misuse in training dataset of usages')
parser.add_argument('-mt','--misuseInTest', action='store_true', help='detects misuse in test dataset')
parser.add_argument('-md','--misuseFdoc', action='store_true', help='detects misuse from API documentation')
args = parser.parse_args()
source = args.trainfile
destination = args.testfile
	
#Only generate patterns
if args.pattern:
	if os.path.exists(source):
		generate_patterns(source,destination,'NoMisuseDetection')
	else:
		print('Training Dataset folder doesnot exists')

#Finding Misuse in train dataset itself
elif args.misuseInUsage:

	if os.path.exists(source):
		generate_patterns(source,destination,'MisuseDetection')
		flist = fileList(source)
		for fp in flist:
			subprocess.call(['python3','matching.py',destination+'/NoArg_patterns.txt', source+'/'+fp+'_asm.txt',''])
			os.remove(source+'/'+fp+'_asm.txt')
	else:
		print('Train Dataset doesnot exists')

#Generating patterns using train dataset and find misuse in test dataset
elif args.misuseInTest:
	if os.path.exists(source) and os.path.exists(destination):
		generate_patterns(source,destination,'MisuseDetection')
          
		generate_asm(destination)

		flist = fileList(destination)
		for fp in flist:
			subprocess.call(['python3','matching.py',destination+'/NoArg_patterns.txt', destination+'/'+fp+'_asm.txt',''])
			os.remove(destination+'/'+fp+'_asm.txt')

		tflist = fileList(source)
		for fpt in tflist:
			os.remove(source+'/'+fpt+'_asm.txt')

	elif os.path.exists(source):
		print('Test Dataset doesnot exists')
	elif os.path.exists(destination):
		print('Training Dataset doesnot exists')

#Finding API misuse against contraint example of Documentation
elif args.misuseFdoc:
	if os.path.exists(source) and os.path.exists(destination):
		generate_asm(source)
		flist = fileList(source)
		for fp in flist:
			with open(source+'/'+fp+'_asm.txt') as jfile: 
				data=json.load(jfile)
			with open(source+'/'+fp+'_ASM_WithNoArguments_MACHINES.txt','w') as fr:
				json.dump([data[1]],fr)
			subprocess.call(['python3','pattern.py',source+'/'+fp+'_ASM_WithNoArguments_MACHINES',destination+'/'+fp+'_NoArg','DOC'])

			generate_asm(destination)
			testfp = fileList(destination)
			for fpt in testfp:
				subprocess.call(['python3','matching.py',destination+'/'+fp+'_NoArg_patterns.txt', destination+'/'+fpt+'_asm.txt','DOC'])
				os.remove(destination+'/'+fpt+'_asm.txt')
			os.remove(source+'/'+fp+'_asm.txt')




		
