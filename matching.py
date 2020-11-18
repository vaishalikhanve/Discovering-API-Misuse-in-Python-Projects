import json
import sys
import copy
import os
'''
1. Check neighbour ordering between children of same parent in pattern => by doing machinechildren.remove(ch), which removes tree already found with one child (example: if else)
2. Check parent children ordering (example: APi call ordering)
3. Finds all missing states of ASM (example: all missing API calls)
'''
pattree = {} #stores test machine state 
prevchildren = []
precon = ['if','while']
exitMisuse = ['quit','Quit''close','exit','Exit','destroy']
#Searches given ASM state(pk) in test Machine State(machinechildren)
childlist,pklist = [],[]
def searchInMachine(machinechildren,asm,machine,pk,Statecheck):
	if machinechildren in childlist:
		if pk in pklist:
			return Statecheck, machinechildren;
		else:
			pklist.append(pk)
	else:
		childlist.append(machinechildren)
	for ch in machinechildren:
		Statecheck = search(asm,machine,pk,ch,Statecheck)
		if Statecheck[str(pk)] == 1:
			machinechildren.remove(ch)
			break
		
	return Statecheck, machinechildren;

#finds if states of ASM and test Machine are same or not
def search(asm,machine,k,i,Statecheck):
	
	#ASM reaches its last state 'stop' or test machine reaches one of its endpoints
	if str(i) == '0' or asm[str(k)]['label'] == 'stop':
		return Statecheck
	elif asm[str(k)]['label']==machine[str(i)]['label']:#if ASM state matches with current test machine state
			Statecheck[str(k)] = 1				#update dictionary
			machinechildren = machine[str(i)]['children']
			
			for pk in asm[str(k)]['children']:		#further traverse very next state of ASM
				Statecheck, machinechildren = searchInMachine(machinechildren,asm,machine,pk,Statecheck)
				if Statecheck[str(pk)] == 0:
					pattree[str(pk)] = machinechildren #if this state doesn't found in machine store test machine State 											#for children state of pattern in 'pattree'
				
			return Statecheck
	
	else:
		
		machinechildren = machine[str(i)]['children']
		Statecheck, machinechildren = searchInMachine(machinechildren,asm,machine,k,Statecheck)
		return Statecheck

def matchASM(machine,asm,Statecheck):
	
	for ch in machine['0']['children']:
		del childlist[:]
		del pklist[:]
		Statecheck = search(asm,machine,1,ch,Statecheck)
	#if any state of pattern doesn't match then we are searching for next state using same parents state information of test machine i.e 		machinechildren' so that we can find next type of violation
	
	for k in asm.keys():
		del childlist[:]
		del pklist[:]
		if Statecheck[str(k)] == 0:
			for grandpk in asm[str(k)]['children']:
				if str(k) in pattree:
					Statecheck, machinechildren = searchInMachine(pattree[str(k)],asm,machine,grandpk,Statecheck) 
					#if next state also doesn't match, we will store current test machine info for further child state
					if Statecheck[str(grandpk)] == 0: 
						pattree[str(grandpk)] = machinechildren
								
	return Statecheck
		
#pdfname = sys.argv[1] #pattern with arguments
pfname = sys.argv[1] #patterns without arguments file name
mfname = sys.argv[2] #machine file name
ifDoc = sys.argv[3]
#dfname = sys.argv[4] #ASM from Documentation

ASMs = []
with open(mfname,'r') as kfile: # input graph is stored in json formate
	machines = json.load(kfile)  



with open(pfname,'r') as jfile: # input patterns is stored in json formsate
	all_asm = json.load(jfile)
	
	#tasm = [el for el in all_asm[-2]] 
	tasm = [obj for el in all_asm for obj in el]
	#print(tasm)
	for asm in tasm: # here [-2]  is for last second stage of pattern
		k = int(max(asm.keys()))+1
		v={}
		v['parent'] = [k-1]
		v['children'] = []
		v['label'] = 'stop'
		asm[str(k)] = v
		ASMs.append(asm)
	
filename = mfname.split('/')[-1].split('.')[0][:-4]
'''with open('label_key.txt','r') as lfile:
	label_key = json.load(lfile)'''


Violationlist = {}
print(mfname)
#Find Violation in each ASM
for asm in ASMs:
	machine = copy.deepcopy(machines[1]) #machines[1] because non argument state present in 2nd index of indiviual usage ASM file
	ind = ASMs.index(asm)
	#print(asm)
	Statecheck = {}
	for k in asm.keys():
		Statecheck[str(k)] = 0
	Statecheck = matchASM(machine,asm,Statecheck)
	del Statecheck[str(max([int(sp) for sp in Statecheck]))]
	Violationlist[ind] = Statecheck
	
# Find all predecessor states of given state

def upperstates(sm,k,sl):

	if sm[str(k)]['parent']==[] or sm[str(k)]['children']==[0]:
		return sl
	for ck in sm[str(k)]['parent']:
		obj = {}
		obj[str(sm[str(ck)]['label'])]=str(ck)
		sl.append(obj)
		sl = upperstates(sm,ck,sl)
	return sl

# Find all sucessor state of given state
def lowerstates(sm,k,sl):
	if sm[str(k)]['children']==[] or sm[str(k)]['children']==[0]:
		return sl
	for ck in sm[str(k)]['children']:
		
		obj = {}
		obj[str(sm[str(ck)]['label'])]=str(ck)
		sl.append(obj)
		sl = lowerstates(sm,ck,sl)
	return sl

# Create Misuse report using misuse classification
machine = copy.deepcopy(machines[1])
report = '** Misuse Report of '+filename+'**\n\n'
for vobject in Violationlist:
	vasm = ASMs[vobject]
	
	if ifDoc == 'DOC':
		report += 'API State Machine generated from Documentation example '+str(vobject)+'\n'
	else:
		report += 'Pattern number:- '+str(vobject)+'\n'
	use = 0
	for sv in Violationlist[vobject]:
		if Violationlist[vobject][sv]==0:
			
			flag=0
			for mv in machine:
				if machine[mv]['label']==vasm[str(sv)]['label']:
					if (int(sv)-1>=1 and vasm[str(int(sv)-1)]['label']!=vasm[str(sv)]['label']) and ((int(sv)+1<=max([int(sp) for sp in Statecheck])) and vasm[str(int(sv)+1)]['label']!=vasm[str(sv)]['label']):
						asmu = upperstates(vasm,sv,[]) #predecessor states of violated obj sv in ASM
						machu = upperstates(machine,mv,[])#predecessor states of machine label in test machine
						
						asml = lowerstates(vasm,sv,[]) #sucessor states in ASM
						machl = lowerstates(machine,mv,[]) #predecessor states in machine
						
						#intersection/common state present in predecessor states of ASM and sucessor states of Machine
						ix = [set([list(k.keys())[0] for k in asmu]) & set([list(k.keys())[0] for k in machl])]
						#intersection state present in predecessor states of machines and sucessor states of ASM
						iy = [set([list(k.keys())[0] for k in machu]) & set([list(k.keys())[0] for k in asml])]						
						#should be used after
						if ix!=[set()]:
							for x in ix:
								for xl in machl:
									if list(x)[0] in dict(xl):
										flag=1
										#print('exchange state of ',mv,dict(xl)[list(x)[0]])
										report+='Misusetype: Incorrect order of method call at positions - '+str(mv)+','+str(dict(xl)[list(x)[0]])+'\nThis method call-"'+vasm[str(sv)]['label']+'" should have been used after "'+str(list(x)[0])+'"\n'
						
						#Should be used before
						if iy!=[set()]:
							for y in iy:
								for yu in machu:
									if list(y)[0] in dict(yu):
									
										#print('exchange state of ',mv,dict(yu)[list(y)[0]])
										flag=1
										report+='Misusetype: Incorrect order of method call at positions - '+str(mv)+','+str(dict(yu)[list(y)[0]])+'\n This method call-"'+vasm[str(sv)]['label']+'" should have been used before "'+str(list(y)[0])+'"\n'
			
			if flag==0:
				#print('missing method calls',vasm[str(sv)]['label'])
				findexit = [vasm[str(sv)]['label'].find(ctag)>-1 for ctag in exitMisuse]
                                findcond = [vasm[str(sv)]['label'].find(ctag)>-1 for ctag in precon]
				if True in findexit:
					report+='Misusetype: Missing closing condition of state - '+str(sv)+' : '+vasm[str(sv)]['label']+'\n'
				elif True in findcond:
                                        report+='Misusetype: Missing pre condition of state - '+str(sv)+' : '+vasm[str(sv)]['label']+'\n'
				else:
					report+='Misusetype: Missing Method calls of state - '+str(sv)+' : '+vasm[str(sv)]['label']+'\n'
				flag=1
			use=flag
	if use==0:
		report+='No misuse\n'
report+='\n\n\n'
mfname = mfname.split('/')
rname = '/'.join(mfname[:-1])
with open(rname+'/'+ifDoc+'report.txt','a') as fp:
	fp.write(report)
print(report)
