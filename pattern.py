#Pattern mining algorithm
import operator
import json
import sys

machineLabel = []
label_key = []
fname = sys.argv[1]
doc = sys.argv[3]
# input ASMs stored in json formate in file-fname
with open(fname+'.txt','r') as jfile:   
	machines=json.load(jfile)

#store each train machine labels
def createLab():			
	for m in machines:
		lab = []
		for k in m.keys():
			lab.append(m[str(k)]['label'])
		machineLabel.append(lab)


#find frequency of each item present in list
def frequent(flist,flag,num):		
	if doc == 'DOC':
		num=1
	fdict = {}
	count, itm = 0, ''
	for item in flist:
		fdict[str(item)] = flist.count(item)
	fre1  = dict(sorted(fdict.items(),key = operator.itemgetter(1),reverse=True))
	if flag==1:
		return dict((k,v) for k, v in fre1.items() if v>=num)
	else:
		return dict((k,v) for k, v in fre1.items() if v==num)


#Find if given subpattern present in given machine
def findPattern_in_machines(asm,m):
	c=0
	
	for i in range(1,len(asm.keys())+1):
		lab = asm[str(i)]['label']
		
		if lab in m:
			c+=1
	
	if c == len(asm.keys()):
		return True
	return False

#Check if subASM present in sufficient number of machine
def checkSubASM(subASMs,machineLab,nnode):
	patterns = []
	
	for asm in subASMs:
		asmcount = 0                                       #number of asm containing given pattern
		for m in machineLab:
			if findPattern_in_machines(asm,m) == True: # find presence of pattern in a machine
				asmcount+=1
		
		if (asmcount >= 2) or doc == 'DOC':		   #minimum number of machine required to approve pattern
			patterns.append(asm)
	return frequent(patterns,1,2)
	






#generates f1 sub graph
def createf1subgraph():
	f1=[]
	
	for sm in machines:
		
		key= sorted(sm.keys())
		label ={}
		#print(sm,'\n')
		for k in key:
			if k!='0' and sm[str(k)]['children']!=[0]:
				for c in sm[str(k)]['children']:
					g,v1,v2 = {},{},{}
					#node1 of f1 ASM
					v1['parent'] = []
					v1['children'] = [2]
					v1['label'] = sm[str(k)]['label']
					g['1'] = v1
				 
					#node2 of f1 ASM
					v2['parent'] = [1]
					v2['children'] = []
					v2['label'] = sm[str(c)]['label']
					g['2'] = v2
					f1.append(g)
			label[str(sm[str(k)]['label'])] = k
		label_key.append(label)
	fre1 = frequent(f1,1,2)        #include only frequent subASM
	
	f1subgraph = []
	for d in fre1:
		if d not in f1subgraph:
			f1subgraph.append(eval(d))
	return f1subgraph

# Create ASM state and attach it to start or end state to extend ASM by one state
def create(obj,fsub,flag,gedge):
	g = {}  #ASM object
	for i in range(1,gedge+2):
		
		v = {}
		#if state attach in front of existing start state
		if flag == 0:	
			#start state
			if i==1: 
				v['parent'] = []
				v['children'] = [i+1]
				v['label'] = obj['label']
			#end state
			elif i==gedge+1: 
				v['parent'] = [gedge]
				v['children'] = []
				v['label'] = fsub[str(gedge)]['label']
			#inbetween states
			else:			
				v['parent'] = [i-1]
				v['children'] = [i+1]
				v['label'] = fsub[str(i-1)]['label']
		
		#if state attach to the back of existing end state
		elif flag == 1:  
			
			if i==1:
				v['parent'] = []
				v['children'] = [i+1]
				v['label'] = fsub['1']['label']

			elif i==gedge+1:
				v['parent'] = [gedge]
				v['children'] = []
				v['label'] = obj['label']
			else:
				v['parent'] = [i-1]
				v['children'] = [i+1]
				v['label'] = fsub[str(i)]['label']	
		g[str(i)] = v
	return g

# Check given of object in list
def findInList(item,fsg_list):
	for obj in fsg_list:
		objflag = 0
		for k in obj.keys():
			if obj[str(k)]['label'] != item[str(k)]['label'] or obj[str(k)]['parent'] != item[str(k)]['parent'] or obj[str(k)]['children'] != item[str(k)]['children']:
				objflag=1
				break

		if objflag==0:
			return False
	return True


# add all sucessor of end state and all predecessor of start state one at a time to extend pattern by one 
neighlist = []
def addneighbour(machine,in_key,fsub,flag,gedge,fsg):
	#return if recurring
	if in_key in neighlist:
		return fsg

	nobj = create(machine[str(in_key)],fsub,flag,gedge)
	neighlist.append(in_key)

	#check if given subASM already present
	if findInList(nobj,fsg):
		fsg.append(nobj)
	
	#add to start state
	if flag == 0:
		for p in machine[str(in_key)]['parent']:
			if p != 0 and machine[str(in_key)]['label']!=machine[str(p)]['label']:
				fsg = addneighbour(machine,p,fsub,flag,gedge,fsg)
	#extend to end state 
	elif flag ==1:
		for c in machine[str(in_key)]['children']:
			if c != 0 and machine[str(in_key)]['label']!=machine[str(c)]['label']:
				fsg = addneighbour(machine,c,fsub,flag,gedge,fsg)
	
	return fsg

#Extend exisiting subASM by one using its neighbour or by all predecessors and sucessors
def nedgeGraph(gedge,fsubgraph,machines):
	fsg = []
	for sm in machines:
		
		for f in fsubgraph:
			f0label = f['1']['label']
			f1label = f[str(gedge)]['label']
			label = label_key[machines.index(sm)]
			nitem = []

			#add state to start state using predecessors of start state
			if str(f0label) in label.keys():
				k = label[str(f0label)]
				for p in sm[k]['parent']:
					if p != 0 and sm[k]['label']!=sm[str(p)]['label']:
						#next two lines generates patterns using all sucessors and predecessors
						#nitem = addneighbour(sm,p,f,0,gedge,fsg)
						#del neighlist[:]
						fsg.append(create(sm[str(p)],f,0,gedge)) #get pattern from neighbours
						

			#add state to end state using sucessors of end state
			if str(f1label) in label.keys():
				k = label[str(f1label)]
				for c in sm[k]['children']:
					if c != 0 and sm[k]['label']!=sm[str(c)]['label']:
						#next two lines generates patterns using all sucessors and predecessors
						#nitem = addneighbour(sm,c,f,1,gedge,fsg)
						#del neighlist[:]
						fsg.append(create(sm[str(c)],f,1,gedge)) #get pattern from neighbours

			#check existence of newly formed pattern in existing list 
			'''for ni in nitem:
				if findInList(ni,fsg):
					fsg.append(ni)'''
				
	return fsg


#Find out frequent ASMs present in the train dataset
def findASMpattern():
	all_patterns = []
	#generate smallest possible subASM
	fprevSubGraphs = createf1subgraph()
	prev=1
	all_patterns.append(fprevSubGraphs)

	#recurssively generate bigger size frequent ASMs
	while len(fprevSubGraphs)!=0:
		#extend existing subASM by one state 
		fgraph = nedgeGraph(prev+1,fprevSubGraphs,machines) 
		#checking if extended ASM pattern belongs to maximum number of training dataset
		fre2 = checkSubASM(fgraph,machineLabel,prev+1)	
		fsubgraph = []
		for d in fre2:
			fsubgraph.append(eval(d)) 
		prev+=1
		fprevSubGraphs = fsubgraph
		all_patterns.append(fsubgraph)	
	return all_patterns	

#Main function calls
createLab()	
all_patterns = findASMpattern()
all_patterns = all_patterns[:-1]

if doc == 'DOC':
	all_patterns = [all_patterns[-1]]
	print(all_patterns)
else:
	#remove unnecessary small frequent ASMs
	if len(all_patterns)>2:
		all_patterns = all_patterns[-2:]
	greatest_pattern = all_patterns[-1]
	smallest_pattern = all_patterns[-2]

	#remove small subASM present in larger patterns 
	for gp in greatest_pattern:
		gplist = []
		for i in gp.keys():
			gplist.append(gp[str(i)]['label'])
		gp1 = gplist[:-1]
		gp2 = gplist[1:]
		for sp in smallest_pattern:
			f1,f2 = 0,0 
			for i in range(1,len(gplist)):
				if gp1[i-1]!=sp[str(i)]['label']:
					f1=1
				
				if gp2[i-1]!=sp[str(i)]['label']:
					f2=1
	
				if f1==1 & f2==1:
					break
			if f1==0 or f2==0:
				all_patterns[-2].pop(smallest_pattern.index(sp))
		

'''with open('label_key.txt','w')as ofile:
	json.dump(label_key,ofile)'''
#Store identified frequent ASMs 
with open(sys.argv[2]+'_patterns.txt','w') as outfile:
	json.dump(all_patterns,outfile)
print('Frequent ASM generated for Multipart API: ',all_patterns)
	
